from tests import BaseTestCase


class CharacterHelperTest(BaseTestCase):
    """
    There are currently no helpers for character only tests
    """


class JournalHelperTest(BaseTestCase):
    def test_gen_session_choices(self, app, client):
        from app.character.helpers import gen_session_choices

        self.set_up_users()
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()
        self.set_up_sessions()

        # char_admin_priv has no sessions -> only "none"
        # char_user has 2 sessions
        # all others have one session
        self.assertEqual(len(gen_session_choices(self.char_admin)), 2)
        self.assertEqual(len(gen_session_choices(self.char_admin_priv)), 1)

        self.assertEqual(len(gen_session_choices(self.char_moderator)), 2)
        self.assertEqual(len(gen_session_choices(self.char_moderator_priv)), 2)

        self.assertEqual(len(gen_session_choices(self.char_user)), 3)
        self.assertEqual(len(gen_session_choices(self.char_user_priv)), 2)
