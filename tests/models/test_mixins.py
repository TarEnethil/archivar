from tests import BaseTestCase
from app import db
from app.mixins import LinkGenerator, PermissionTemplate, ProfilePicture, SimpleChangeTracker, SimplePermissionChecker

######
# DB Test classes
######


class LG(db.Model, LinkGenerator):
    id = db.Column(db.Integer, primary_key=True)


class PT(db.Model, PermissionTemplate):
    id = db.Column(db.Integer, primary_key=True)


class PP(db.Model, ProfilePicture):
    id = db.Column(db.Integer, primary_key=True)


class SCT(db.Model, SimpleChangeTracker):
    id = db.Column(db.Integer, primary_key=True)
    flag = db.Column(db.Boolean)


class SPC(db.Model, SimplePermissionChecker):
    id = db.Column(db.Integer, primary_key=True)


######
# Base Test Case
######

class BaseMixinTestCase(BaseTestCase):
    """
    Base class for testing mixins
    """
    def setUp(self, app, client):
        from app.main.models import GeneralSetting

        super().setUp(app, client)

        """
        need to re-create all tables as we define new db.Model classes in this file
        """
        self.db.drop_all()
        self.db.create_all()

        # fake 'install' so that login works again
        self.general_setting = GeneralSetting(world_name="Testworld")
        self.add(self.general_setting)
        self.commit()


######
# Test classes start here
######

class SimpleChangeTrackerTest(BaseMixinTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()

    def test_created(self, app, client):
        from datetime import datetime

        no_creator = SCT()
        self.add(no_creator)
        self.commit()

        self.assertIsNone(no_creator.created_by)

        now = datetime.utcnow()
        delta = now - no_creator.created
        self.assertLess(delta.total_seconds(), 1.0)

        self.login(client, self.admin)
        with_creator = SCT()
        self.add(with_creator)
        self.commit()

        self.assertEqual(self.admin, with_creator.created_by)

    def test_edited(self, app, client):
        from datetime import datetime

        no_editor = SCT()
        self.add(no_editor)
        self.commit()

        self.login(client, self.admin)
        with_editor = SCT()
        self.add(with_editor)
        self.commit()

        self.assertIsNone(no_editor.edited)
        self.assertIsNone(no_editor.edited_by)
        self.assertIsNone(with_editor.edited)
        self.assertIsNone(with_editor.edited_by)

        self.logout(client)
        no_editor.flag = True
        self.commit()

        self.assertIsNone(no_editor.edited_by)
        now = datetime.utcnow()
        delta = now - no_editor.edited
        self.assertLess(delta.total_seconds(), 1.0)

        self.login(client, self.admin)
        with_editor.flag = True
        self.commit()

        self.assertEqual(self.admin, with_editor.edited_by)
        now = datetime.utcnow()
        delta = now - with_editor.edited
        self.assertLess(delta.total_seconds(), 1.0)

    def test_print_info(self, app, client):
        from flask_login import login_user

        obj = SCT()
        self.add(obj)
        self.commit()

        with app.test_request_context("/"):
            info = obj.print_info(context={})
            self.assertTrue("Created" in info)
            self.assertFalse("Edited" in info)
            self.assertTrue("on" in info)
            self.assertFalse("by" in info)

            obj.flag = True
            self.commit()
            info = obj.print_info(context={})
            self.assertTrue("Created" in info)
            self.assertTrue("Edited" in info)
            self.assertTrue("on" in info)
            self.assertFalse("by" in info)

        self.login(client, self.admin)

        self.admin.dateformat = "YYYY"
        obj = SCT()
        self.add(obj)
        self.commit()

        with app.test_request_context("/"):
            info = obj.print_info(context={})
            self.assertTrue("Created" in info)
            self.assertFalse("Edited" in info)
            self.assertTrue("on" in info)
            self.assertTrue("by" in info)
            self.assertTrue("format('LLL')" in info)  # default value for unauthenticated users

            obj.flag = True
            self.commit()
            login_user(self.admin)  # need extra login within request_context
            info = obj.print_info(context={})
            self.assertTrue("Created" in info)
            self.assertTrue("Edited" in info)
            self.assertTrue("on" in info)
            self.assertTrue("by" in info)

            # check for default params and dateformat
            self.assertTrue("<hr" in info)
            self.assertTrue("format('YYYY')" in info)

            info = obj.print_info(context={}, create=False)
            self.assertFalse("Created" in info)
            self.assertTrue("Edited" in info)

            info = obj.print_info(context={}, edit=False)
            self.assertTrue("Created" in info)
            self.assertFalse("Edited" in info)

            info = obj.print_info(context={}, hr=False)
            self.assertFalse("<hr" in info)


class PermissionTemplateTest(BaseMixinTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()

        self.pt = PT()
        self.add(self.pt)
        self.commit()

    def test_is_editable_by_user(self, app, client):
        with self.assertRaises(NotImplementedError):
            self.pt.is_editable_by_user()

    def test_is_deletable_by_user(self, app, client):
        with self.assertRaises(NotImplementedError):
            self.pt.is_deletable_by_user()


class SimplePermissionCheckerTest(BaseMixinTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()

        self.spc = SPC()
        self.add(self.spc)
        self.invis_spc = SPC(is_visible=False)
        self.add(self.invis_spc)
        self.commit()

    def set_up_user_spc(self, client):
        self.login(client, self.user)
        self.user_spc = SPC()
        self.add(self.user_spc)
        self.invis_user_spc = SPC(is_visible=False)
        self.add(self.invis_user_spc)
        self.commit()

    def test_is_viewable_by_user(self, app, client):
        with self.assertRaises(NotImplementedError):
            self.spc.is_viewable_by_user()

    def test_is_owned_by_user(self, app, client):
        self.login(client, self.user)
        user_spc = SPC()
        self.add(user_spc)
        self.commit()

        self.assertFalse(self.spc.is_owned_by_user())
        self.assertTrue(user_spc.is_owned_by_user())

    def test_is_hideable_by_user(self, app, client):
        self.set_up_user_spc(client)  # implicitly logs in as 'user'

        self.assertFalse(self.spc.is_hideable_by_user())
        self.assertTrue(self.user_spc.is_hideable_by_user())

    def test_get_query_for_visible_items(self, app, client):
        from flask_login import login_user

        # need request context for current_user (?)
        with app.test_request_context("/"):
            query = SPC.get_query_for_visible_items()
            spcs = query.all()

            self.assertEqual(len(spcs), 1)
            self.assertTrue(self.spc in spcs)

            query = SPC.get_query_for_visible_items(include_hidden_for_user=True)
            spcs = query.all()

            self.assertEqual(len(spcs), 1)
            self.assertTrue(self.spc in spcs)

        self.set_up_user_spc(client)

        with app.test_request_context("/"):
            login_user(self.user)  # extra login within request context needed
            query = SPC.get_query_for_visible_items()
            spcs = query.all()

            self.assertEqual(len(spcs), 2)
            self.assertTrue(self.spc in spcs)
            self.assertTrue(self.user_spc in spcs)

            query = SPC.get_query_for_visible_items(include_hidden_for_user=True)
            spcs = query.all()

            self.assertEqual(len(spcs), 3)
            self.assertTrue(self.spc in spcs)
            self.assertTrue(self.user_spc in spcs)
            self.assertTrue(self.invis_user_spc in spcs)

    def test_get_visible_items(self, app, client):
        from flask_login import login_user

        # need request context for current_user (?)
        with app.test_request_context("/"):
            spcs = SPC.get_visible_items()

            self.assertEqual(len(spcs), 1)
            self.assertTrue(self.spc in spcs)

            spcs = SPC.get_visible_items(include_hidden_for_user=True)

            self.assertEqual(len(spcs), 1)
            self.assertTrue(self.spc in spcs)

        self.set_up_user_spc(client)

        with app.test_request_context("/"):
            login_user(self.user)  # extra login within request context needed
            spcs = SPC.get_visible_items()

            self.assertEqual(len(spcs), 2)
            self.assertTrue(self.spc in spcs)
            self.assertTrue(self.user_spc in spcs)

            spcs = SPC.get_visible_items(include_hidden_for_user=True)

            self.assertEqual(len(spcs), 3)
            self.assertTrue(self.spc in spcs)
            self.assertTrue(self.user_spc in spcs)
            self.assertTrue(self.invis_user_spc in spcs)

    def test_default_value(self, app, client):
        self.assertTrue(self.spc.is_visible)
        self.assertFalse(self.invis_spc.is_visible)


class LinkGeneratorTest(BaseMixinTestCase):
    """
    all the link functions are already tested in test_app_helpers
    as such, we don't test much here
    """
    def setUp(self, app, client):
        super().setUp(app, client)

        self.lg = LG()
        self.add(self.lg)
        self.commit()

    def test_default(self, app, client):
        with self.assertRaises(NotImplementedError):
            self.lg.view_url()

        with self.assertRaises(NotImplementedError):
            self.lg.edit_url()

        with self.assertRaises(NotImplementedError):
            self.lg.delete_url()


class ProfilePictureTest(BaseMixinTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.pp = PP()
        self.add(self.pp)
        self.commit()

    def test_infobox(self, app, client):
        with self.assertRaises(NotImplementedError):
            self.pp.infobox()

    def test_profile_picture_url(self, app, client):
        with app.test_request_context("/"):
            self.assertTrue("no_profile.png" in self.pp.profile_picture_url())

        self.pp.profile_picture = "pp.png"
        self.commit()

        with app.test_request_context("/"):
            self.assertTrue("pp.png" in self.pp.profile_picture_url())

    def test_profile_thumbnail_url(self, app, client):
        with app.test_request_context("/"):
            self.assertTrue("no_profile.png" in self.pp.profile_thumbnail_url())

        self.pp.profile_picture = "pp.png"
        self.commit()

        with app.test_request_context("/"):
            self.assertTrue("pp.png" in self.pp.profile_thumbnail_url())
            self.assertTrue("thumb" in self.pp.profile_thumbnail_url())
