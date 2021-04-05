from tests import SmokeWrapper


class UserSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def set_up_common_urls(self):
        self.common_urls = [self.admin.view_url(), self.moderator.view_url(), self.user.view_url()]
        self.common_endpoints = ["user.password"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, self.admin.edit_url(), url=True)
        self.assertHTTPOK(client, self.moderator.edit_url(), url=True)
        self.assertHTTPOK(client, self.user.edit_url(), url=True)
        self.assertHTTPOK(client, "user.list")
        self.assertHTTPOK(client, "user.create")
        self.assertHTTPOK(client, "user.settings")

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.moderator.edit_url(), url=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.user.edit_url(), url=True)
