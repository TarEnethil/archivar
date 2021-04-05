from tests import BaseTestCase


class UserModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()

    def test_set_password(self, app, client):
        """
        Test that setting the password works as expected.
        """
        self.user.set_password("Test#$$1337!")

        self.assertTrue(self.user.check_password("Test#$$1337!"))
        self.assertFalse(self.user.check_password("different_password"))

    def test_roles(self, app, client):
        """
        Test that role-evaluating functions are working
        """
        u = self.admin
        self.assertTrue(u.is_admin())
        self.assertFalse(u.is_moderator())
        self.assertFalse(u.is_user())
        self.assertTrue(u.is_at_least_moderator())

        u = self.moderator
        self.assertFalse(u.is_admin())
        self.assertTrue(u.is_moderator())
        self.assertFalse(u.is_user())
        self.assertTrue(u.is_at_least_moderator())

        u = self.user
        self.assertFalse(u.is_admin())
        self.assertFalse(u.is_moderator())
        self.assertTrue(u.is_user())
        self.assertFalse(u.is_at_least_moderator())

    def test_permissions(self, app, client):
        """
        Test that permissions for this class are working as expected.
        User only has is_editable_by_user() at the moment.
        """
        self.login(client, self.admin)
        self.assertTrue(self.admin.is_editable_by_user())
        self.assertTrue(self.moderator.is_editable_by_user())
        self.assertTrue(self.user.is_editable_by_user())

        self.login(client, self.moderator)
        self.assertFalse(self.admin.is_editable_by_user())
        self.assertTrue(self.moderator.is_editable_by_user())
        self.assertFalse(self.user.is_editable_by_user())

        self.login(client, self.user)
        self.assertFalse(self.admin.is_editable_by_user())
        self.assertFalse(self.moderator.is_editable_by_user())
        self.assertTrue(self.user.is_editable_by_user())

        self.login(client, self.user2)
        self.assertFalse(self.admin.is_editable_by_user())
        self.assertFalse(self.moderator.is_editable_by_user())
        self.assertFalse(self.user.is_editable_by_user())

        # Test that is_deletable raises NotImpelemented (only need to check one character)
        # is_viewable and is_hideable are not part of model User
        self.assertNotImplemented(self.user.is_deletable_by_user)

    def test_get_characters(self, app, client):
        """
        Test get_characters(), which gets the _viewable_ characters.
        Thus, we have to test with different people logged in.
        """
        self.set_up_characters()

        # check admin
        self.login(client, self.admin)
        chars = self.admin.get_characters()
        self.assertEqual(len(chars), 2)
        self.assertIn(self.char_admin, chars)
        self.assertIn(self.char_admin_priv, chars)

        chars = self.moderator.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_moderator, chars)

        chars = self.user.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_user, chars)

        chars = self.user2.get_characters()
        self.assertEqual(len(chars), 0)

        # check moderator
        self.login(client, self.moderator)
        chars = self.admin.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_admin, chars)

        chars = self.moderator.get_characters()
        self.assertEqual(len(chars), 2)
        self.assertIn(self.char_moderator, chars)
        self.assertIn(self.char_moderator_priv, chars)

        chars = self.user.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_user, chars)

        # check user
        self.login(client, self.user)
        chars = self.admin.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_admin, chars)

        chars = self.moderator.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_moderator, chars)

        chars = self.user.get_characters()
        self.assertEqual(len(chars), 2)
        self.assertIn(self.char_user, chars)
        self.assertIn(self.char_user_priv, chars)

        # check user2
        self.login(client, self.user2)
        chars = self.admin.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_admin, chars)

        chars = self.moderator.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_moderator, chars)

        chars = self.user.get_characters()
        self.assertEqual(len(chars), 1)
        self.assertIn(self.char_user, chars)

    def test_has_char_in_party(self, app, client):
        """
        Test that has_char_in_party() works as expected.
        """
        self.set_up_characters()
        self.set_up_parties()

        self.assertTrue(self.admin.has_char_in_party(self.party1))
        self.assertFalse(self.admin.has_char_in_party(self.party2))
        self.assertFalse(self.admin.has_char_in_party(self.party3))

        self.assertTrue(self.moderator.has_char_in_party(self.party1))
        self.assertTrue(self.moderator.has_char_in_party(self.party2))
        self.assertFalse(self.moderator.has_char_in_party(self.party3))

        self.assertFalse(self.user.has_char_in_party(self.party1))
        self.assertTrue(self.user.has_char_in_party(self.party2))
        self.assertTrue(self.user.has_char_in_party(self.party3))

        self.assertFalse(self.user2.has_char_in_party(self.party1))
        self.assertFalse(self.user2.has_char_in_party(self.party2))
        self.assertFalse(self.user2.has_char_in_party(self.party3))

    def test_is_dm_of(self, app, client):
        """
        Test that is_dm_of() is working as expected.
        """
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()

        self.assertTrue(self.admin.is_dm_of(self.campaign1))
        self.assertFalse(self.admin.is_dm_of(self.campaign2))
        self.assertFalse(self.admin.is_dm_of(self.campaign3))

        self.assertFalse(self.moderator.is_dm_of(self.campaign1))
        self.assertTrue(self.moderator.is_dm_of(self.campaign2))
        self.assertFalse(self.moderator.is_dm_of(self.campaign3))

        self.assertFalse(self.user.is_dm_of(self.campaign1))
        self.assertFalse(self.user.is_dm_of(self.campaign2))
        self.assertTrue(self.user.is_dm_of(self.campaign3))

        self.assertFalse(self.user2.is_dm_of(self.campaign1))
        self.assertFalse(self.user2.is_dm_of(self.campaign2))
        self.assertFalse(self.user2.is_dm_of(self.campaign3))

    def test_is_dm_of_anything(self, app, client):
        """
        Test that is_dm_of_anything() is working as expected.
        """
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()

        self.assertTrue(self.admin.is_dm_of_anything())
        self.assertTrue(self.moderator.is_dm_of_anything())
        self.assertTrue(self.user.is_dm_of_anything())
        self.assertFalse(self.user2.is_dm_of_anything())

    def test_has_char_in_session(self, app, client):
        """
        Test that has_char_in_session() is working as expected.
        """
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()
        self.set_up_sessions()

        self.assertFalse(self.admin.has_char_in_session(self.session1))
        self.assertFalse(self.admin.has_char_in_session(self.session2))
        self.assertTrue(self.admin.has_char_in_session(self.session3))

        self.assertTrue(self.moderator.has_char_in_session(self.session1))
        self.assertFalse(self.moderator.has_char_in_session(self.session2))
        self.assertTrue(self.moderator.has_char_in_session(self.session3))

        self.assertTrue(self.user.has_char_in_session(self.session1))
        self.assertTrue(self.user.has_char_in_session(self.session2))
        self.assertFalse(self.user.has_char_in_session(self.session3))

        self.assertFalse(self.user2.has_char_in_session(self.session1))
        self.assertFalse(self.user2.has_char_in_session(self.session2))
        self.assertFalse(self.user2.has_char_in_session(self.session3))

    def test_participated_campaigns(self, app, client):
        """
        Test that participated_campaigns() is working as expected.
        """
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()
        self.set_up_sessions()

        campaigns = self.admin.participated_campaigns()
        self.assertEqual(len(campaigns), 1)
        self.assertIn(self.campaign3, campaigns)

        campaigns = self.moderator.participated_campaigns()
        self.assertEqual(len(campaigns), 2)
        self.assertIn(self.campaign1, campaigns)
        self.assertIn(self.campaign3, campaigns)

        campaigns = self.user.participated_campaigns()

        self.assertEqual(len(campaigns), 3)
        self.assertIn(self.campaign1, campaigns)
        self.assertIn(self.campaign2, campaigns)
        self.assertIn(self.campaign3, campaigns)

    def test_is_assoc_dm_of_party(self, app, client):
        """
        Test that participated_campaigns() is working as expected.
        """
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()
        self.set_up_sessions()

        self.assertFalse(self.admin.is_assoc_dm_of_party(self.party1))
        self.assertTrue(self.admin.is_assoc_dm_of_party(self.party2))
        self.assertFalse(self.admin.is_assoc_dm_of_party(self.party3))

        self.assertFalse(self.moderator.is_assoc_dm_of_party(self.party1))
        self.assertFalse(self.moderator.is_assoc_dm_of_party(self.party2))
        self.assertTrue(self.moderator.is_assoc_dm_of_party(self.party3))

        self.assertTrue(self.user.is_assoc_dm_of_party(self.party1))
        self.assertFalse(self.user.is_assoc_dm_of_party(self.party2))
        self.assertFalse(self.user.is_assoc_dm_of_party(self.party3))

        self.assertFalse(self.user2.is_assoc_dm_of_party(self.party1))
        self.assertFalse(self.user2.is_assoc_dm_of_party(self.party2))
        self.assertFalse(self.user2.is_assoc_dm_of_party(self.party3))
