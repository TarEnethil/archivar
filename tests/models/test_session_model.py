from tests import BaseTestCase


class SessionModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()
        self.set_up_sessions()

    def test_permissions(self, app, client):
        """
        Test that permissions for this class are working as expected.
        """

        ########
        # Admin
        ########
        # should be able to edit & delete all
        self.login(client, self.admin)
        self.assertTrue(self.session1.is_editable_by_user())
        self.assertTrue(self.session2.is_editable_by_user())
        self.assertTrue(self.session3.is_editable_by_user())
        self.assertTrue(self.session4.is_editable_by_user())

        self.assertTrue(self.session1.is_deletable_by_user())
        self.assertTrue(self.session2.is_deletable_by_user())
        self.assertTrue(self.session3.is_deletable_by_user())
        self.assertTrue(self.session4.is_deletable_by_user())

        ############
        # Moderator
        ############
        # Participated in sessions 1 and 3, DM of Session 2
        self.login(client, self.moderator)
        self.assertTrue(self.session1.is_editable_by_user())
        self.assertTrue(self.session2.is_editable_by_user())
        self.assertTrue(self.session3.is_editable_by_user())
        self.assertFalse(self.session4.is_editable_by_user())

        self.assertFalse(self.session1.is_deletable_by_user())
        self.assertTrue(self.session2.is_deletable_by_user())
        self.assertFalse(self.session3.is_deletable_by_user())
        self.assertFalse(self.session4.is_deletable_by_user())

        #######
        # User
        #######
        # Participated in sessions 1, 2 and 4, DM of Session 3 and 4
        self.login(client, self.user)
        self.assertTrue(self.session1.is_editable_by_user())
        self.assertTrue(self.session2.is_editable_by_user())
        self.assertTrue(self.session3.is_editable_by_user())
        self.assertTrue(self.session4.is_editable_by_user())

        self.assertFalse(self.session1.is_deletable_by_user())
        self.assertFalse(self.session2.is_deletable_by_user())
        self.assertTrue(self.session3.is_deletable_by_user())
        self.assertTrue(self.session4.is_deletable_by_user())

        self.session1.participants.remove(self.char_user)
        self.commit()

        self.assertFalse(self.session1.is_editable_by_user())

        ########
        # User2
        ########
        # Participated in no session, DM of no session
        self.login(client, self.user2)
        self.assertFalse(self.session1.is_editable_by_user())
        self.assertFalse(self.session2.is_editable_by_user())
        self.assertFalse(self.session3.is_editable_by_user())
        self.assertFalse(self.session4.is_editable_by_user())

        self.assertFalse(self.session1.is_deletable_by_user())
        self.assertFalse(self.session2.is_deletable_by_user())
        self.assertFalse(self.session3.is_deletable_by_user())
        self.assertFalse(self.session4.is_deletable_by_user())
