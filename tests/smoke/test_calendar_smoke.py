
from flask import url_for
from tests import SmokeWrapper


class CalendarSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def test_reachability_admin(self, app, client):
        self.set_up_calendar()
        self.login(client, self.admin)

        self.assertHTTPOK(client, "calendar.settings")
        self.assertHTTPOK(client, "calendar.index", follow=True)
        self.assertHTTPOK(client, "calendar.view")
        self.assertHTTPOK(client, "calendar.check", follow=True)
        self.assertHTTPOK(client, "calendar.preview")

        # finalize and check some urls again without follow
        self.assertHTTPOK(client, "calendar.finalize", follow=True)
        self.assertHTTPOK(client, "calendar.index")
        self.assertHTTPOK(client, "calendar.view")

    def test_reachability_moderator(self, app, client):
        self.set_up_calendar(finalized=True)
        self.login(client, self.moderator)

        self.assertHTTPOK(client, "calendar.index")
        self.assertHTTPOK(client, "calendar.view")

    def test_reachability_user(self, app, client):
        self.set_up_calendar(finalized=True)
        self.login(client, self.user)

        self.assertHTTPOK(client, "calendar.index")
        self.assertHTTPOK(client, "calendar.view")


class EpochSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_calendar()

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "calendar.epoch_create")
        self.assertHTTPOK(client, self.epochs[0].edit_url(), url=True)
        self.assertHTTPOK(client, url_for("calendar.epoch_up", id=self.epochs[1].id, name="x"),
                          url=True, follow=True)
        self.assertHTTPOK(client, url_for("calendar.epoch_down", id=self.epochs[1].id, name="x"),
                          url=True, follow=True)
        self.assertHTTPOK(client, url_for("calendar.epoch_delete", id=self.epochs[0].id, name="x"),
                          url=True, follow=True)


class MonthSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_calendar()

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "calendar.month_create")
        self.assertHTTPOK(client, self.months[0].edit_url(), url=True)
        self.assertHTTPOK(client, url_for("calendar.month_up", id=self.months[1].id, name="x"),
                          url=True, follow=True)
        self.assertHTTPOK(client, url_for("calendar.month_down", id=self.months[1].id, name="x"),
                          url=True, follow=True)
        self.assertHTTPOK(client, url_for("calendar.month_delete", id=self.months[0].id, name="x"),
                          url=True, follow=True)


class DaySmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_calendar()

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "calendar.day_create")
        self.assertHTTPOK(client, self.days[0].edit_url(), url=True)
        self.assertHTTPOK(client, url_for("calendar.day_up", id=self.days[1].id, name="x"),
                          url=True, follow=True)
        self.assertHTTPOK(client, url_for("calendar.day_down", id=self.days[1].id, name="x"),
                          url=True, follow=True)
        self.assertHTTPOK(client, url_for("calendar.day_delete", id=self.days[0].id, name="x"),
                          url=True, follow=True)


class MoonSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_calendar()

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "calendar.moon_create")
        self.assertHTTPOK(client, self.moons[0].edit_url(), url=True)
        self.assertHTTPOK(client, url_for("calendar.moon_delete", id=self.moons[0].id, name="x"),
                          url=True, follow=True)
