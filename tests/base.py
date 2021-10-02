import flask_unittest
import os
from config.default_config import DefaultConfig
from app import create_app as create_archivar_app
from app import db
from app.processors import register_processors_and_filters
from app.helpers import Role
from app.calendar.models import CalendarSetting, Epoch, Month, Day, Moon
from app.campaign.models import Campaign
from app.character.models import Character, Journal
from app.event.models import Event, EventCategory
from app.main.models import GeneralSetting
from app.map.models import Map, MapNode, MapNodeType
from app.media.models import MediaItem, MediaCategory
from app.party.models import Party
from app.random.models import RandomTable, RandomTableEntry
from app.session.models import Session
from app.user.models import User
from app.wiki.models import WikiEntry
from flask import url_for
from flask_login import current_user
from shutil import copyfile

root_testdir = os.path.abspath(os.path.dirname(__file__))


class TestConfig(DefaultConfig):
    TESTING = True
    SECRET_KEY = "NotSoSecret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
    WTF_CSRF_ENABLED = False


class FakeFile(object):
    """
    Fake object class that can be used like data from a file-upload form field
    """
    def __init__(self, filename, upload_should_fail=False):
        self.filename = filename
        self.upload_should_fail = upload_should_fail
        self.rootdir = root_testdir

    def save(self, filepath):
        """
        'save' an image (copy an existing image to the requested path)
        or fail with an exception to test failure cases
        """
        if (self.upload_should_fail is True):
            raise Exception("FakeFile: Upload failed intentionally")
        else:
            copyfile(os.path.join(self.rootdir, self.filename), filepath)


class FakeField(object):
    """
    Fake object for single form fields (used to test validators)
    """
    def __init__(self, name, data):
        self.name = name
        self.data = data


class FakeForm(object):
    """
    Fake object for forms (used to test validators)
    """
    def __init__(self, fields):
        self._fields = {}
        for f in fields:
            self._fields[f.name] = f


class BaseTestCase(flask_unittest.AppClientTestCase):
    def create_app(self):
        return create_archivar_app(TestConfig)

    def setUp(self, app, client):
        register_processors_and_filters(app)

        self.app_context = app.app_context()
        self.app_context.push()

        self.db = db
        self.db.create_all()

        # fake 'install' so that login works
        self.general_setting = GeneralSetting(world_name="Testworld")
        self.add(self.general_setting)
        self.commit()

    def tearDown(self, app, client):
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()

    def add(self, obj):
        self.db.session.add(obj)

    def add_all(self, objs):
        self.db.session.add_all(objs)

    def rem(self, obj):
        self.db.session.delete(obj)

    def rem_all(self, objs):
        for obj in objs:
            self.rem(obj)

    def commit(self):
        self.db.session.commit()

    def assertNotImplemented(self, func):
        try:
            func()
        except NotImplementedError:
            return
        except Exception:
            self.assertFalse(True, "Wrong exception type raised")

        self.assertFalse(True, f"No exception raised during {func.__name__}")

    def logout(self, client):
        client.get('/logout', follow_redirects=True)
        self.assertFalse(current_user.is_authenticated)

    def login(self, client, user):
        if (current_user and current_user.is_authenticated):
            if current_user != user:
                self.logout(client)

        user.set_password("test")
        client.post('/login', data=dict(username=user.username, password="test"), follow_redirects=True)

        self.assertTrue(current_user == user)

    def set_up_users(self):
        self.admin = User(username="Admin", role=Role.Admin.value)
        self.moderator = User(username="Moderator", role=Role.Moderator.value)
        self.user = User(username="User")
        self.user2 = User(username="User2")

        self.add_all([self.admin, self.moderator, self.user, self.user2])
        self.commit()

    def set_up_characters(self):
        self.char_admin = Character(name="Char Admin 1", user_id=self.admin.id)
        self.char_admin_priv = Character(name="Char Admin 2", user_id=self.admin.id, is_visible=False)

        self.char_moderator = Character(name="Char Moderator 1", user_id=self.moderator.id)
        self.char_moderator_priv = Character(name="Char Moderator 2", user_id=self.moderator.id, is_visible=False)

        self.char_user = Character(name="Char User 1", user_id=self.user.id)
        self.char_user_priv = Character(name="Char User 2", user_id=self.user.id, is_visible=False)

        self.add_all([self.char_admin, self.char_admin_priv,
                      self.char_moderator, self.char_moderator_priv,
                      self.char_user, self.char_user_priv])
        self.commit()

    def set_up_journals(self):
        self.journal_admin = Journal(title="Journal Admin", character_id=self.char_admin.id)
        self.journal_admin_priv = Journal(title="Journal Admin Priv", character_id=self.char_admin.id, is_visible=False)

        self.journal_moderator = Journal(title="Journal Moderator", character_id=self.char_moderator.id)
        self.journal_moderator_priv = Journal(title="Journal Moderator Priv", character_id=self.char_moderator.id,
                                              is_visible=False)

        self.journal_user = Journal(title="Journal User", character_id=self.char_user.id)
        self.journal_user_priv = Journal(title="Journal User Priv", character_id=self.char_user.id, is_visible=False)

        self.add_all([self.journal_admin, self.journal_admin_priv,
                      self.journal_moderator, self.journal_moderator_priv,
                      self.journal_user, self.journal_user_priv])
        self.commit()

    def set_up_parties(self):
        self.party1 = Party(name="Party 1", members=[self.char_admin, self.char_moderator_priv])
        self.party2 = Party(name="Party 2", members=[self.char_moderator, self.char_user])
        self.party3 = Party(name="Party 3", members=[self.char_user_priv])

        self.add_all([self.party1, self.party2, self.party3])
        self.commit()

    def set_up_campaigns(self):
        self.campaign1 = Campaign(name="Campaign 1", dm_id=self.admin.id,
                                  associated_parties=[self.party2])
        self.campaign2 = Campaign(name="Campaign 2", dm_id=self.moderator.id,
                                  associated_parties=[self.party3])
        self.campaign3 = Campaign(name="Campaign 3", dm_id=self.user.id,
                                  associated_parties=[self.party1])

        self.add_all([self.campaign1, self.campaign2, self.campaign3])
        self.commit()

    def set_up_sessions(self):
        from datetime import date
        self.session1 = Session(title="Session 1", campaign_id=self.campaign1.id,
                                participants=[self.char_moderator, self.char_user], date=date(2000, 1, 1))
        self.session2 = Session(title="Session 2", campaign_id=self.campaign2.id,
                                participants=[self.char_user_priv], date=date(2001, 1, 1))
        self.session3 = Session(title="Session 3", campaign_id=self.campaign3.id,
                                participants=[self.char_admin, self.char_moderator_priv], date=date(2002, 1, 1))
        self.session4 = Session(title="Session 4", campaign_id=self.campaign3.id,
                                participants=[self.char_user], date=date(2003, 1, 1))

        self.add_all([self.session1, self.session2, self.session3, self.session4])
        self.commit()

    def set_up_media(self):
        self.media_cat1 = MediaCategory(name="Media Category 1")
        self.media_cat2 = MediaCategory(name="Media Category 2")
        self.media_cat3 = MediaCategory(name="Media Category 3")

        self.add_all([self.media_cat1, self.media_cat2, self.media_cat3])
        self.commit()

        self.media1 = MediaItem(name="Media 1", filename="test.pdf",
                                created_by_id=self.admin.id, category_id=self.media_cat1.id)
        self.media2 = MediaItem(name="Media 2", filename="test.png",
                                created_by_id=self.admin.id, is_visible=False, category_id=self.media_cat1.id)
        self.media3 = MediaItem(name="Media 3", filename="test.jpg",
                                created_by_id=self.moderator.id, category_id=self.media_cat1.id)
        self.media4 = MediaItem(name="Media 4", filename="test.tar",
                                created_by_id=self.moderator.id, is_visible=False, category_id=self.media_cat2.id)
        self.media5 = MediaItem(name="Media 5", filename="test.tar.bz2",
                                created_by_id=self.user.id, category_id=self.media_cat2.id)
        self.media6 = MediaItem(name="Media 6", filename="test.zip",
                                created_by_id=self.user.id, is_visible=False, category_id=self.media_cat3.id)

        self.add_all([self.media1, self.media2, self.media3, self.media4, self.media5, self.media6])
        self.commit()

    def set_up_wiki(self):
        self.wiki_entry1 = WikiEntry(title="Wiki 1", created_by_id=self.admin.id, category="Cat 1")
        self.wiki_entry2 = WikiEntry(title="Wiki 2", created_by_id=self.admin.id, category="Cat 1",
                                     is_visible=False)
        self.wiki_entry3 = WikiEntry(title="Wiki 3", created_by_id=self.moderator.id, category="Cat 1")
        self.wiki_entry4 = WikiEntry(title="Wiki 4", created_by_id=self.moderator.id, category="Cat 2",
                                     is_visible=False)
        self.wiki_entry5 = WikiEntry(title="Wiki 5", created_by_id=self.user.id, category="")
        self.wiki_entry6 = WikiEntry(title="Wiki 6", created_by_id=self.user.id, category="", is_visible=False)

        self.add_all([self.wiki_entry1, self.wiki_entry2, self.wiki_entry3, self.wiki_entry4,
                      self.wiki_entry5, self.wiki_entry6])
        self.commit()

    def set_up_epochs(self):
        epoch1 = Epoch(name="Epoch 1", abbreviation="E1", years=100, order=1)
        epoch2 = Epoch(name="Epoch 2", abbreviation="E2", years=200, order=2)
        epoch3 = Epoch(name="Epoch 3", years=0, order=3)

        self.epochs = [epoch1, epoch2, epoch3]
        self.add_all(self.epochs)
        self.commit()

    def set_up_months(self):
        month1 = Month(name="Month 1", abbreviation="M1", days=10, order=1)
        month2 = Month(name="Month 2", abbreviation="M2",  days=20, order=2)
        month3 = Month(name="Month 3", days=30, order=3)
        month4 = Month(name="Month 4", abbreviation="M4",  days=40, order=4)

        self.months = [month1, month2, month3, month4]
        self.add_all(self.months)
        self.commit()

    def set_up_days(self):
        day1 = Day(name="Day 1", abbreviation="D1", order=1)
        day2 = Day(name="Day 2", abbreviation="D2", order=2)
        day3 = Day(name="Day 3", abbreviation="D3", order=3)
        day4 = Day(name="Day 4", order=4)
        day5 = Day(name="Day 5", abbreviation="D5", order=5)

        self.days = [day1, day2, day3, day4, day5]
        self.add_all(self.days)
        self.commit()

    def set_up_moons(self):
        moon1 = Moon(name="Moon 1", phase_length=8, phase_offset=0)
        moon2 = Moon(name="Moon 2", phase_length=8, phase_offset=4)
        moon3 = Moon(name="Moon 3", phase_length=15, phase_offset=0)

        self.moons = [moon1, moon2, moon3]
        self.add_all(self.moons)
        self.commit()

    def set_up_calendar(self, finalized=False):
        self.add(CalendarSetting(finalized=finalized))
        self.commit()

        self.set_up_epochs()
        self.set_up_months()
        self.set_up_days()
        self.set_up_moons()

        # do and commit calculations for epochs and months
        if finalized:
            from app.calendar.helpers import gen_calendar_preview_data
            gen_calendar_preview_data(commit=True)

    def set_up_events(self, timestamps=True):
        self.event_cat1 = EventCategory(name="Event Category 1")
        self.event_cat2 = EventCategory(name="Event Category 2")
        self.event_cat3 = EventCategory(name="Event Category 3")

        self.add_all([self.event_cat1, self.event_cat2, self.event_cat3])
        self.commit()

        self.event1 = Event(name="Event 1", epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id,
                            day=1, duration=1, created_by_id=self.admin.id, category_id=self.event_cat1.id)
        self.event2 = Event(name="Event 2", epoch_id=self.epochs[0].id, year=2, month_id=self.months[1].id,
                            day=2, duration=2, created_by_id=self.admin.id, is_visible=False,
                            category_id=self.event_cat1.id)
        self.event3 = Event(name="Event 3", epoch_id=self.epochs[0].id, year=3, month_id=self.months[2].id,
                            day=3, duration=3, created_by_id=self.moderator.id, category_id=self.event_cat1.id)
        self.event4 = Event(name="Event 4", epoch_id=self.epochs[1].id, year=101, month_id=self.months[3].id,
                            day=10, duration=1, created_by_id=self.moderator.id, is_visible=False,
                            category_id=self.event_cat2.id)
        self.event5 = Event(name="Event 5", epoch_id=self.epochs[1].id, year=102, month_id=self.months[3].id,
                            day=11, duration=1, created_by_id=self.user.id,
                            category_id=self.event_cat2.id)
        self.event6 = Event(name="Event 6", epoch_id=self.epochs[2].id, year=301, month_id=self.months[2].id,
                            day=4, duration=1, created_by_id=self.user.id, is_visible=False,
                            category_id=self.event_cat3.id)

        self.add_all([self.event1, self.event2, self.event3, self.event4, self.event5, self.event6])
        self.commit()

        if timestamps:
            from app.event.helpers import update_timestamp
            update_timestamp(self.event1.id)
            update_timestamp(self.event2.id)
            update_timestamp(self.event3.id)
            update_timestamp(self.event4.id)
            update_timestamp(self.event5.id)
            update_timestamp(self.event6.id)

    def set_up_maps(self):
        self.map1 = Map(name="Map 1", created_by_id=self.admin.id)
        self.map2 = Map(name="Map 2", created_by_id=self.admin.id, is_visible=False)
        self.add_all([self.map1, self.map2])
        self.commit()

    def set_up_map_nodes(self):
        self.map_node_type1 = MapNodeType(name="Map Node Type 1", icon_file="test.jpg")
        self.map_node_type2 = MapNodeType(name="Map Node Type 2", icon_file="test.jpg")

        self.add_all([self.map_node_type1, self.map_node_type2])
        self.commit()

        self.map_node1 = MapNode(name="Map Node 1", created_by_id=self.admin.id, on_map=self.map1.id,
                                 node_type=self.map_node_type1.id)
        self.map_node2 = MapNode(name="Map Node 2", created_by_id=self.admin.id, on_map=self.map1.id,
                                 node_type=self.map_node_type1.id, is_visible=False)
        self.map_node3 = MapNode(name="Map Node 3", created_by_id=self.moderator.id, on_map=self.map1.id,
                                 node_type=self.map_node_type1.id)
        self.map_node4 = MapNode(name="Map Node 4", created_by_id=self.moderator.id, on_map=self.map1.id,
                                 node_type=self.map_node_type2.id, is_visible=False)
        self.map_node5 = MapNode(name="Map Node 5", created_by_id=self.user.id, on_map=self.map1.id,
                                 node_type=self.map_node_type2.id)
        self.map_node6 = MapNode(name="Map Node 6", created_by_id=self.user.id, on_map=self.map1.id,
                                 node_type=self.map_node_type2.id, is_visible=False)

        self.add_all([self.map_node1, self.map_node2, self.map_node3, self.map_node4, self.map_node5, self.map_node6])
        self.commit()

    def set_up_random_tables(self):
        self.random_table1 = RandomTable(name="Table 1", created_by_id=self.admin.id)
        self.random_table2 = RandomTable(name="Table 2", created_by_id=self.moderator.id)
        self.random_table3 = RandomTable(name="Table 3", created_by_id=self.user.id)

        self.add_all([self.random_table1, self.random_table2, self.random_table3])
        self.commit()

        entry1 = RandomTableEntry(title="Entry1", weight=1, table_id=self.random_table1.id,
                                  created_by_id=self.admin.id)
        entry2 = RandomTableEntry(title="Entry2", weight=2, table_id=self.random_table1.id,
                                  created_by_id=self.moderator.id)
        entry3 = RandomTableEntry(title="Entry3", weight=3, table_id=self.random_table2.id,
                                  created_by_id=self.admin.id)
        entry4 = RandomTableEntry(title="Entry4", weight=3, table_id=self.random_table2.id,
                                  created_by_id=self.user.id)
        entry5 = RandomTableEntry(title="Entry5", weight=5, table_id=self.random_table2.id,
                                  created_by_id=self.moderator.id)
        entry6 = RandomTableEntry(title="Entry6", weight=100, table_id=self.random_table2.id,
                                  created_by_id=self.admin.id)

        self.random_table_entries = [entry1, entry2, entry3, entry4, entry5, entry6]
        self.add_all(self.random_table_entries)
        self.commit()


class SmokeWrapper:
    """
    Wrap SmokeTestCase in wrapper, so that test_reachability_common() only gets
    executed for the child classes.
    See: https://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class/25695512#25695512
    """
    class SmokeTestCase(BaseTestCase):
        def setUp(self, app, client):
            super().setUp(app, client)

            self.set_up_users()
            self.admin.must_change_password = False
            self.moderator.must_change_password = False
            self.user.must_change_password = False

            self.commit()

        def set_up_common_urls(self):
            """
            default implementation
            """
            self.common_urls = None
            self.common_endpoints = None

        def assertHTTPOK(self, client, endpoint, url=False, follow=False, get=True):
            if url is False:
                endpoint = url_for(endpoint)

            if get:
                r = client.get(endpoint, follow_redirects=follow)
            else:
                r = client.post(endpoint, follow_redirects=follow)

            if current_user.is_authenticated:
                user = current_user.username
            else:
                user = "unauthenticated user"

            self.assertEqual(r.status_code, 200, f"{endpoint} failed for user {user}")

        def test_reachability_common(self, app, client):
            # TODO: figure out why this is needed or if we can do this another way
            with app.test_request_context("/"):
                self.set_up_common_urls()

            if self.common_urls is None and self.common_endpoints is None:
                return  # prevent unnecessary logins

            for user in [self.admin, self.moderator, self.user]:
                self.login(client, user)

                if self.common_urls:
                    for url in self.common_urls:
                        self.assertHTTPOK(client, url, url=True)

                if self.common_endpoints:
                    for ep in self.common_endpoints:
                        self.assertHTTPOK(client, ep)
