from flask import url_for
from tests import SmokeWrapper


class SessionSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()
        self.set_up_sessions()

    def set_up_common_urls(self):
        self.common_urls = [self.session1.view_url(), self.session2.view_url(), self.session3.view_url(),
                            self.session3.view_url()]
        self.common_endpoints = ["session.index"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "session.create")

        self.assertHTTPOK(client, url_for("session.create_with_campaign", id=self.campaign1.id), url=True)

        self.assertHTTPOK(client, self.session1.edit_url(), url=True)
        self.assertHTTPOK(client, self.session2.edit_url(), url=True)
        self.assertHTTPOK(client, self.session3.edit_url(), url=True)

        self.assertHTTPOK(client, self.session1.delete_url(), url=True, follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, "session.create", follow=True)

        self.assertHTTPOK(client, url_for("session.create_with_campaign", id=self.campaign2.id), url=True)

        self.assertHTTPOK(client, self.session1.edit_url(), url=True)
        self.assertHTTPOK(client, self.session2.edit_url(), url=True)
        self.assertHTTPOK(client, self.session3.edit_url(), url=True)

        self.assertHTTPOK(client, self.session2.delete_url(), url=True, follow=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, "session.create", follow=True)

        self.assertHTTPOK(client, url_for("session.create_with_campaign", id=self.campaign3.id), url=True)

        self.assertHTTPOK(client, self.session1.edit_url(), url=True)
        self.assertHTTPOK(client, self.session2.edit_url(), url=True)
        self.assertHTTPOK(client, self.session3.edit_url(), url=True)

        self.assertHTTPOK(client, self.session3.delete_url(), url=True, follow=True)
