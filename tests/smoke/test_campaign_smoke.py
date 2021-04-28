from flask import url_for
from tests import SmokeWrapper


class CampaignSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()

    def set_up_common_urls(self):
        self.common_urls = [self.campaign1.view_url(), self.campaign2.view_url(), self.campaign3.view_url(),
                            url_for("campaign.timeline", id=self.campaign1.id, name="x"),
                            url_for("campaign.timeline", id=self.campaign2.id, name="x"),
                            url_for("campaign.timeline", id=self.campaign3.id, name="x")]
        self.common_endpoints = ["campaign.index"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "campaign.create")

        self.assertHTTPOK(client, self.campaign1.edit_url(), url=True)
        self.assertHTTPOK(client, self.campaign2.edit_url(), url=True)
        self.assertHTTPOK(client, self.campaign3.edit_url(), url=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.campaign2.edit_url(), url=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.campaign3.edit_url(), url=True)
