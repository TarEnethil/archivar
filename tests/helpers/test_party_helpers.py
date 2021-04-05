from tests import BaseTestCase


class PartyHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)
        self.set_up_users()
        self.set_up_characters()

    def test_gen_party_members_choices(self, app, client):
        from app.party.helpers import gen_party_members_choices

        self.assertEqual(len(gen_party_members_choices()), 3)
        self.assertEqual(len(gen_party_members_choices(ensure=[self.char_user])), 3)
        self.assertEqual(len(gen_party_members_choices(ensure=[self.char_admin_priv])), 4)

        all_invis_chars = [self.char_admin_priv, self.char_moderator_priv, self.char_user_priv]
        self.assertEqual(len(gen_party_members_choices(ensure=all_invis_chars)), 6)

    def test_gen_party_choices(self, app, client):
        from app.party.helpers import gen_party_choices

        self.set_up_parties()

        self.assertEqual(len(gen_party_choices()), 3)
