from app.event.models import EventSetting
from flask import url_for
from tests import SmokeWrapper


class EventSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_calendar(finalized=True)
        self.set_up_events()

        self.add(EventSetting(default_category=self.event_cat1.id))
        self.commit()

    def set_up_common_urls(self):
        self.common_urls = [self.event1.view_url(), self.event3.view_url(), self.event5.view_url(),
                            self.event1.edit_url(), self.event3.edit_url(), self.event5.edit_url(),
                            url_for("event.list_epoch", e_id=self.epochs[0].id, e_name="x"),
                            url_for("event.list_epoch_year", e_id=self.epochs[0].id, e_name="x", year=1),
                            url_for("event.list_category", c_id=self.event_cat1.id, c_name="x")]
        self.common_endpoints = ["event.list", "event.create"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, self.event1.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.event2.view_url(), url=True)
        self.assertHTTPOK(client, self.event2.edit_url(), url=True)
        self.assertHTTPOK(client, self.event2.delete_url(), url=True, follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.event3.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.event4.view_url(), url=True)
        self.assertHTTPOK(client, self.event4.edit_url(), url=True)
        self.assertHTTPOK(client, self.event4.delete_url(), url=True, follow=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.event5.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.event6.view_url(), url=True)
        self.assertHTTPOK(client, self.event6.edit_url(), url=True)
        self.assertHTTPOK(client, self.event6.delete_url(), url=True, follow=True)


class EventCategorySmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_calendar(finalized=True)
        self.set_up_events()

        self.add(EventSetting(default_category=self.event_cat1.id))
        self.commit()

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "event.category_create")
        self.assertHTTPOK(client, url_for("event.category_edit", id=self.event_cat1.id, name="x"), url=True)
        self.assertHTTPOK(client, "event.settings")

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, "event.category_create")
        self.assertHTTPOK(client, url_for("event.category_edit", id=self.event_cat1.id, name="x"), url=True)
        self.assertHTTPOK(client, "event.settings")

    def test_reachability_user(self, app, client):
        self.login(client, self.user)
        pass
