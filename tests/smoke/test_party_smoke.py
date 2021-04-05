from tests import SmokeWrapper


class PartySmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_characters()
        self.set_up_parties()

    def set_up_common_urls(self):
        self.common_urls = [self.party1.view_url(), self.party2.view_url(), self.party3.view_url()]
        self.common_endpoints = None

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "party.create")

        self.assertHTTPOK(client, self.party1.edit_url(), url=True)

        self.assertHTTPOK(client, self.party1.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.party2.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.party3.delete_url(), url=True, follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.party1.edit_url(), url=True)
        self.assertHTTPOK(client, self.party2.edit_url(), url=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.party2.edit_url(), url=True)
        self.assertHTTPOK(client, self.party3.edit_url(), url=True)
