from tests import SmokeWrapper


class MainSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def set_up_common_urls(self):
        self.common_urls = []
        self.common_endpoints = ["main.index", "main.about", "main.changelog", "main.statistics"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "main.settings")
        self.assertHTTPOK(client, "main.logout", follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, "main.settings")
        self.assertHTTPOK(client, "main.logout", follow=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)
        self.assertHTTPOK(client, "main.logout", follow=True)

    def test_reachability_not_authenticated(self, app, client):
        self.logout(client)

        self.assertHTTPOK(client, "main.about")
        self.assertHTTPOK(client, "main.changelog")
        self.assertHTTPOK(client, "main.index", follow=True)

        self.rem(self.general_setting)
        self.commit()

        self.assertHTTPOK(client, "main.install")
        self.assertHTTPOK(client, "main.index", follow=True)
