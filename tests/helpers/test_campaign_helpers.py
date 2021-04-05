from tests import BaseTestCase


class CampaignHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()

    def test_gen_dm_choices(self, app, client):
        from app.campaign.helpers import gen_dm_choices

        self.assertEqual(len(gen_dm_choices()), 4)  # all users

    def test_gen_campaign_choices_dm(self, app, client):
        from app.campaign.helpers import gen_campaign_choices_dm

        self.login(client, self.moderator)
        self.assertEqual(len(gen_campaign_choices_dm()), 1)
        self.assertEqual(gen_campaign_choices_dm()[0][1], self.campaign2.name)

        self.login(client, self.user)
        self.assertEqual(len(gen_campaign_choices_dm()), 1)
        self.assertEqual(gen_campaign_choices_dm()[0][1], self.campaign3.name)

        self.campaign1.dm_id = self.user.id
        self.commit()
        self.assertEqual(len(gen_campaign_choices_dm()), 2)

        self.login(client, self.user2)
        self.assertEqual(len(gen_campaign_choices_dm()), 0)

    def test_campaign_choices_admin(self, app, client):
        from app.campaign.helpers import gen_campaign_choices_admin

        self.login(client, self.admin)
        self.assertEqual(len(gen_campaign_choices_admin()), 3)
