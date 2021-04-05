from tests import BaseTestCase


class CampaignModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()

    def test_permissions(self, app, client):
        """
        Test that permissions for this class are working as expected.
        """

        ########
        # Admin
        ########
        # DM of campaign 1
        self.login(client, self.admin)
        self.assertTrue(self.campaign1.is_editable_by_user())
        self.assertTrue(self.campaign2.is_editable_by_user())
        self.assertTrue(self.campaign3.is_editable_by_user())

        ############
        # Moderator
        ############
        # DM of campaign 2
        self.login(client, self.moderator)
        self.assertFalse(self.campaign1.is_editable_by_user())
        self.assertTrue(self.campaign2.is_editable_by_user())
        self.assertFalse(self.campaign3.is_editable_by_user())

        #######
        # User
        #######
        # DM of campaign 3
        self.login(client, self.user)
        self.assertFalse(self.campaign1.is_editable_by_user())
        self.assertFalse(self.campaign2.is_editable_by_user())
        self.assertTrue(self.campaign3.is_editable_by_user())

        ########
        # User2
        ########
        # Not a DM
        self.login(client, self.user2)
        self.assertFalse(self.campaign1.is_editable_by_user())
        self.assertFalse(self.campaign2.is_editable_by_user())
        self.assertFalse(self.campaign3.is_editable_by_user())

        self.assertNotImplemented(self.campaign1.is_deletable_by_user)
