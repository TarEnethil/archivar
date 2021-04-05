from tests import BaseTestCase


class CharacterModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_characters()

    def test_get_journals(self, app, client):
        """
        get_journals() is affected by visibility, thus we need to login
        """
        self.set_up_journals()

        self.login(client, self.admin)
        self.assertEqual(len(self.char_admin.get_journals()), 2)
        self.assertEqual(len(self.char_moderator.get_journals()), 1)
        self.assertEqual(len(self.char_user.get_journals()), 1)

        self.login(client, self.moderator)
        self.assertEqual(len(self.char_admin.get_journals()), 1)
        self.assertEqual(len(self.char_moderator.get_journals()), 2)
        self.assertEqual(len(self.char_user.get_journals()), 1)

        self.login(client, self.user)
        self.assertEqual(len(self.char_admin.get_journals()), 1)
        self.assertEqual(len(self.char_moderator.get_journals()), 1)
        self.assertEqual(len(self.char_user.get_journals()), 2)

        self.login(client, self.user2)
        self.assertEqual(len(self.char_admin.get_journals()), 1)
        self.assertEqual(len(self.char_moderator.get_journals()), 1)
        self.assertEqual(len(self.char_user.get_journals()), 1)

    def test_permissions(self, app, client):
        """
        Test that permissions for this class are working as expected.
        """

        ########
        # Admin
        ########
        self.login(client, self.admin)
        self.assertTrue(self.char_admin.is_viewable_by_user())
        self.assertTrue(self.char_admin.is_editable_by_user())
        self.assertTrue(self.char_admin.is_hideable_by_user())
        self.assertTrue(self.char_admin.is_deletable_by_user())
        self.assertTrue(self.char_admin.journal_is_creatable_by_user())

        self.assertTrue(self.char_moderator.is_viewable_by_user())
        self.assertFalse(self.char_moderator.is_editable_by_user())
        self.assertFalse(self.char_moderator.is_hideable_by_user())
        self.assertTrue(self.char_moderator.is_deletable_by_user())
        self.assertFalse(self.char_moderator.journal_is_creatable_by_user())

        self.assertTrue(self.char_user.is_viewable_by_user())
        self.assertFalse(self.char_user.is_editable_by_user())
        self.assertFalse(self.char_user.is_hideable_by_user())
        self.assertTrue(self.char_user.is_deletable_by_user())
        self.assertFalse(self.char_user.journal_is_creatable_by_user())

        self.assertTrue(self.char_admin_priv.is_viewable_by_user())
        self.assertFalse(self.char_moderator_priv.is_viewable_by_user())
        self.assertFalse(self.char_user_priv.is_viewable_by_user())

        self.assertFalse(self.char_user_priv.is_deletable_by_user())

        ############
        # Moderator
        ############
        self.login(client, self.moderator)
        self.assertTrue(self.char_admin.is_viewable_by_user())
        self.assertFalse(self.char_admin.is_editable_by_user())
        self.assertFalse(self.char_admin.is_hideable_by_user())
        self.assertFalse(self.char_admin.is_deletable_by_user())
        self.assertFalse(self.char_admin.journal_is_creatable_by_user())

        self.assertTrue(self.char_moderator.is_viewable_by_user())
        self.assertTrue(self.char_moderator.is_editable_by_user())
        self.assertTrue(self.char_moderator.is_hideable_by_user())
        self.assertTrue(self.char_moderator.is_deletable_by_user())
        self.assertTrue(self.char_moderator.journal_is_creatable_by_user())

        self.assertTrue(self.char_user.is_viewable_by_user())
        self.assertFalse(self.char_user.is_editable_by_user())
        self.assertFalse(self.char_user.is_hideable_by_user())
        self.assertFalse(self.char_user.is_deletable_by_user())
        self.assertFalse(self.char_user.journal_is_creatable_by_user())

        self.assertFalse(self.char_admin_priv.is_viewable_by_user())
        self.assertTrue(self.char_moderator_priv.is_viewable_by_user())
        self.assertFalse(self.char_user_priv.is_viewable_by_user())

        self.assertFalse(self.char_user_priv.is_deletable_by_user())

        #######
        # User
        #######
        self.login(client, self.user)
        self.assertTrue(self.char_admin.is_viewable_by_user())
        self.assertFalse(self.char_admin.is_editable_by_user())
        self.assertFalse(self.char_admin.is_hideable_by_user())
        self.assertFalse(self.char_admin.is_deletable_by_user())
        self.assertFalse(self.char_admin.journal_is_creatable_by_user())

        self.assertTrue(self.char_moderator.is_viewable_by_user())
        self.assertFalse(self.char_moderator.is_editable_by_user())
        self.assertFalse(self.char_moderator.is_hideable_by_user())
        self.assertFalse(self.char_moderator.is_deletable_by_user())
        self.assertFalse(self.char_moderator.journal_is_creatable_by_user())

        self.assertTrue(self.char_user.is_viewable_by_user())
        self.assertTrue(self.char_user.is_editable_by_user())
        self.assertTrue(self.char_user.is_hideable_by_user())
        self.assertTrue(self.char_user.is_deletable_by_user())
        self.assertTrue(self.char_user.journal_is_creatable_by_user())

        self.assertFalse(self.char_admin_priv.is_viewable_by_user())
        self.assertFalse(self.char_moderator_priv.is_viewable_by_user())
        self.assertTrue(self.char_user_priv.is_viewable_by_user())

        self.assertTrue(self.char_user_priv.is_deletable_by_user())

        ########
        # User2
        ########
        self.login(client, self.user2)
        self.assertTrue(self.char_admin.is_viewable_by_user())
        self.assertFalse(self.char_admin.is_editable_by_user())
        self.assertFalse(self.char_admin.is_hideable_by_user())
        self.assertFalse(self.char_admin.is_deletable_by_user())
        self.assertFalse(self.char_admin.journal_is_creatable_by_user())

        self.assertTrue(self.char_moderator.is_viewable_by_user())
        self.assertFalse(self.char_moderator.is_editable_by_user())
        self.assertFalse(self.char_moderator.is_hideable_by_user())
        self.assertFalse(self.char_moderator.is_deletable_by_user())
        self.assertFalse(self.char_moderator.journal_is_creatable_by_user())

        self.assertTrue(self.char_user.is_viewable_by_user())
        self.assertFalse(self.char_user.is_editable_by_user())
        self.assertFalse(self.char_user.is_hideable_by_user())
        self.assertFalse(self.char_user.is_deletable_by_user())
        self.assertFalse(self.char_user.journal_is_creatable_by_user())

        self.assertFalse(self.char_admin_priv.is_viewable_by_user())
        self.assertFalse(self.char_moderator_priv.is_viewable_by_user())
        self.assertFalse(self.char_user_priv.is_viewable_by_user())

        self.assertFalse(self.char_user_priv.is_deletable_by_user())


class JournalModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_characters()
        self.set_up_journals()

    def test_permissions(self, app, client):
        """
        Test that permissions for this class are working as expected.
        """

        ########
        # Admin
        ########
        self.login(client, self.admin)
        self.assertTrue(self.journal_admin.is_viewable_by_user())
        self.assertTrue(self.journal_admin.is_editable_by_user())
        self.assertTrue(self.journal_admin.is_hideable_by_user())
        self.assertTrue(self.journal_admin.is_deletable_by_user())

        self.assertTrue(self.journal_moderator.is_viewable_by_user())
        self.assertFalse(self.journal_moderator.is_editable_by_user())
        self.assertFalse(self.journal_moderator.is_hideable_by_user())
        self.assertTrue(self.journal_moderator.is_deletable_by_user())

        self.assertTrue(self.journal_user.is_viewable_by_user())
        self.assertFalse(self.journal_user.is_editable_by_user())
        self.assertFalse(self.journal_user.is_hideable_by_user())
        self.assertTrue(self.journal_user.is_deletable_by_user())

        self.assertTrue(self.journal_admin_priv.is_viewable_by_user())
        self.assertFalse(self.journal_moderator_priv.is_viewable_by_user())
        self.assertFalse(self.journal_user_priv.is_viewable_by_user())

        self.assertFalse(self.journal_user_priv.is_deletable_by_user())

        ############
        # Moderator
        ############
        self.login(client, self.moderator)
        self.assertTrue(self.journal_admin.is_viewable_by_user())
        self.assertFalse(self.journal_admin.is_editable_by_user())
        self.assertFalse(self.journal_admin.is_hideable_by_user())
        self.assertFalse(self.journal_admin.is_deletable_by_user())

        self.assertTrue(self.journal_moderator.is_viewable_by_user())
        self.assertTrue(self.journal_moderator.is_editable_by_user())
        self.assertTrue(self.journal_moderator.is_hideable_by_user())
        self.assertTrue(self.journal_moderator.is_deletable_by_user())

        self.assertTrue(self.journal_user.is_viewable_by_user())
        self.assertFalse(self.journal_user.is_editable_by_user())
        self.assertFalse(self.journal_user.is_hideable_by_user())
        self.assertFalse(self.journal_user.is_deletable_by_user())

        self.assertFalse(self.journal_admin_priv.is_viewable_by_user())
        self.assertTrue(self.journal_moderator_priv.is_viewable_by_user())
        self.assertFalse(self.journal_user_priv.is_viewable_by_user())

        self.assertFalse(self.journal_user_priv.is_deletable_by_user())

        #######
        # User
        #######
        self.login(client, self.user)
        self.assertTrue(self.journal_admin.is_viewable_by_user())
        self.assertFalse(self.journal_admin.is_editable_by_user())
        self.assertFalse(self.journal_admin.is_hideable_by_user())
        self.assertFalse(self.journal_admin.is_deletable_by_user())

        self.assertTrue(self.journal_moderator.is_viewable_by_user())
        self.assertFalse(self.journal_moderator.is_editable_by_user())
        self.assertFalse(self.journal_moderator.is_hideable_by_user())
        self.assertFalse(self.journal_moderator.is_deletable_by_user())

        self.assertTrue(self.journal_user.is_viewable_by_user())
        self.assertTrue(self.journal_user.is_editable_by_user())
        self.assertTrue(self.journal_user.is_hideable_by_user())
        self.assertTrue(self.journal_user.is_deletable_by_user())

        self.assertFalse(self.journal_admin_priv.is_viewable_by_user())
        self.assertFalse(self.journal_moderator_priv.is_viewable_by_user())
        self.assertTrue(self.journal_user_priv.is_viewable_by_user())

        self.assertTrue(self.journal_user_priv.is_deletable_by_user())

        ########
        # User2
        ########
        self.login(client, self.user2)
        self.assertTrue(self.journal_admin.is_viewable_by_user())
        self.assertFalse(self.journal_admin.is_editable_by_user())
        self.assertFalse(self.journal_admin.is_hideable_by_user())
        self.assertFalse(self.journal_admin.is_deletable_by_user())

        self.assertTrue(self.journal_moderator.is_viewable_by_user())
        self.assertFalse(self.journal_moderator.is_editable_by_user())
        self.assertFalse(self.journal_moderator.is_hideable_by_user())
        self.assertFalse(self.journal_moderator.is_deletable_by_user())

        self.assertTrue(self.journal_user.is_viewable_by_user())
        self.assertFalse(self.journal_user.is_editable_by_user())
        self.assertFalse(self.journal_user.is_hideable_by_user())
        self.assertFalse(self.journal_user.is_deletable_by_user())

        self.assertFalse(self.journal_admin_priv.is_viewable_by_user())
        self.assertFalse(self.journal_moderator_priv.is_viewable_by_user())
        self.assertFalse(self.journal_user_priv.is_viewable_by_user())

        self.assertFalse(self.journal_user_priv.is_deletable_by_user())
