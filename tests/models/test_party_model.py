from tests import BaseTestCase


class PartyModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_characters()
        self.set_up_parties()

    def test_permissions(self, app, client):
        """
        Test that permissions for this class are working as expected.
        """

        ########
        # Admin
        ########
        # Member of party1
        self.login(client, self.admin)
        self.assertTrue(self.party1.is_editable_by_user())
        self.assertTrue(self.party1.is_deletable_by_user())

        self.assertTrue(self.party2.is_editable_by_user())
        self.assertTrue(self.party2.is_deletable_by_user())

        self.assertTrue(self.party3.is_editable_by_user())
        self.assertTrue(self.party3.is_deletable_by_user())

        ############
        # Moderator
        ############
        # Member of party1 and party2
        self.login(client, self.moderator)
        self.assertTrue(self.party1.is_editable_by_user())
        self.assertFalse(self.party1.is_deletable_by_user())

        self.assertTrue(self.party2.is_editable_by_user())
        self.assertFalse(self.party2.is_deletable_by_user())

        self.assertFalse(self.party3.is_editable_by_user())
        self.assertFalse(self.party3.is_deletable_by_user())

        #######
        # User
        #######
        # Member of party2 and party3
        self.login(client, self.user)
        self.assertFalse(self.party1.is_editable_by_user())
        self.assertFalse(self.party1.is_deletable_by_user())

        self.assertTrue(self.party2.is_editable_by_user())
        self.assertFalse(self.party2.is_deletable_by_user())

        self.assertTrue(self.party3.is_editable_by_user())
        self.assertFalse(self.party3.is_deletable_by_user())

        ########
        # User2
        ########
        # not a member of any party
        self.login(client, self.user2)
        self.assertFalse(self.party1.is_editable_by_user())
        self.assertFalse(self.party1.is_deletable_by_user())

        self.assertFalse(self.party2.is_editable_by_user())
        self.assertFalse(self.party2.is_deletable_by_user())

        self.assertFalse(self.party3.is_editable_by_user())
        self.assertFalse(self.party3.is_deletable_by_user())

    def test_permissions_with_campaigns(self, app, client):
        """
        Test that permissions for this class are working as expected.
        Campaigns are set up, thus enabling more editing (by associated DM)
        """
        self.set_up_campaigns()

        ########
        # Admin
        ########
        # Member of party1, DM of campaign1=party2
        self.login(client, self.admin)
        self.assertTrue(self.party1.is_editable_by_user())
        self.assertTrue(self.party1.is_deletable_by_user())

        self.assertTrue(self.party2.is_editable_by_user())
        self.assertTrue(self.party2.is_deletable_by_user())

        self.assertTrue(self.party3.is_editable_by_user())
        self.assertTrue(self.party3.is_deletable_by_user())

        ############
        # Moderator
        ############
        # Member of party1 and party2, DM of campaign2=party3
        self.login(client, self.moderator)
        self.assertTrue(self.party1.is_editable_by_user())
        self.assertFalse(self.party1.is_deletable_by_user())

        self.assertTrue(self.party2.is_editable_by_user())
        self.assertFalse(self.party2.is_deletable_by_user())

        self.assertTrue(self.party3.is_editable_by_user())
        self.assertFalse(self.party3.is_deletable_by_user())

        #######
        # User
        #######
        # Member of party2 and party3, DM of campaign3=party1
        self.login(client, self.user)
        self.assertTrue(self.party1.is_editable_by_user())
        self.assertFalse(self.party1.is_deletable_by_user())

        self.assertTrue(self.party2.is_editable_by_user())
        self.assertFalse(self.party2.is_deletable_by_user())

        self.assertTrue(self.party3.is_editable_by_user())
        self.assertFalse(self.party3.is_deletable_by_user())

        ########
        # User2
        ########
        # not a member of any party, not a DM
        self.login(client, self.user2)
        self.assertFalse(self.party1.is_editable_by_user())
        self.assertFalse(self.party1.is_deletable_by_user())

        self.assertFalse(self.party2.is_editable_by_user())
        self.assertFalse(self.party2.is_deletable_by_user())

        self.assertFalse(self.party3.is_editable_by_user())
        self.assertFalse(self.party3.is_deletable_by_user())
