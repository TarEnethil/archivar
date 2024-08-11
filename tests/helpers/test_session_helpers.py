from tests import BaseTestCase


class SessionHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()
        self.set_up_sessions()

    def test_gen_participant_choices(self, app, client):
        from app.session.helpers import gen_participant_choices

        choices = gen_participant_choices()
        self.assertEqual(len(choices), 2)
        self.assertEqual(len(choices[0][1]), 1)  # Party 1
        self.assertEqual(len(choices[1][1]), 2)  # Party 2

        choices2 = gen_participant_choices(ensure=[self.char_admin])
        self.assertEqual(choices, choices2)  # ensure with character that is already visible

        choices = gen_participant_choices(ensure=[self.char_admin_priv])
        self.assertEqual(len(choices), 3)
        self.assertEqual(len(choices[0][1]), 1)  # Party 1
        self.assertEqual(len(choices[1][1]), 2)  # Party 2
        self.assertEqual(len(choices[2][1]), 1)  # No Party

        choices = gen_participant_choices(ensure=[self.char_admin_priv, self.char_moderator_priv, self.char_user_priv])
        self.assertEqual(len(choices), 4)
        self.assertEqual(len(choices[0][1]), 2)  # Party 1
        self.assertEqual(len(choices[1][1]), 2)  # Party 2
        self.assertEqual(len(choices[2][1]), 1)  # Party 3
        self.assertEqual(len(choices[3][1]), 1)  # No Party

    def test_get_previous_session(self, app, client):
        from app.session.helpers import get_previous_session

        self.assertIsNone(get_previous_session(self.session1))

        self.assertEqual(get_previous_session(self.session6), self.session5)

        self.rem(self.session5)
        self.commit()

        self.assertEqual(get_previous_session(self.session6), self.session1)

        self.rem(self.session1)
        self.commit()

        self.assertIsNone(get_previous_session(self.session6))

    def test_get_next_session(self, app, client):
        from app.session.helpers import get_next_session

        self.assertIsNone(get_next_session(self.session8))

        self.assertEqual(get_next_session(self.session6), self.session7)

        self.rem(self.session7)
        self.commit()

        self.assertEqual(get_next_session(self.session6), self.session8)

        self.rem(self.session8)
        self.commit()

        self.assertIsNone(get_next_session(self.session6))

    def test_recalc_session_numbers(self, app, client):
        from app.session.helpers import recalc_session_numbers

        recalc_session_numbers(self.campaign1, self.db)

        self.assertEqual(self.session1.session_number, 1)
        self.assertEqual(self.session5.session_number, 2)
        self.assertEqual(self.session6.session_number, 3)
        self.assertEqual(self.session7.session_number, 4)
        self.assertEqual(self.session8.session_number, 5)

        self.rem(self.session5)
        self.rem(self.session7)
        self.commit()

        recalc_session_numbers(self.campaign1, self.db)

        self.assertEqual(self.session1.session_number, 1)
        self.assertEqual(self.session6.session_number, 2)
        self.assertEqual(self.session8.session_number, 3)

    def test_get_last_session_for_user(self, app, client):
        from app.session.helpers import get_last_session_for_user

        # as DM
        self.login(client, self.admin)
        self.assertEqual(get_last_session_for_user(), self.session8)

        # as character
        self.login(client, self.moderator)
        self.assertEqual(get_last_session_for_user(), self.session8)

        # as character
        self.login(client, self.user)
        self.assertEqual(get_last_session_for_user(), self.session8)

        self.login(client, self.user2)
        self.assertIsNone(get_last_session_for_user())

    def test_get_next_session_for_user(self, app, client):
        from app.session.helpers import get_next_session_for_user

        # no session in future at the start
        for u in [self.admin, self.moderator, self.user, self.user2]:
            self.login(client, u)
            self.assertIsNone(get_next_session_for_user())

        # add session in future
        from app.session.models import Session
        from datetime import date
        session9 = Session(title="Session 9", campaign_id=self.campaign1.id,
                           participants=[self.char_moderator, self.char_user], date=date(2099, 1, 1))

        self.add(session9)
        self.commit()

        # as DM
        self.login(client, self.admin)
        self.assertEqual(get_next_session_for_user(), session9)

        # as character
        self.login(client, self.moderator)
        self.assertEqual(get_next_session_for_user(), session9)

        # as character
        self.login(client, self.user)
        self.assertEqual(get_next_session_for_user(), session9)

        self.login(client, self.user2)
        self.assertIsNone(get_next_session_for_user())

    def set_up_sessions(self):
        """
        Set up a few extra sessions for campaign 1, so that
        we can properly test stuff.
        """
        super().set_up_sessions()

        from app.session.models import Session
        from datetime import date

        self.session5 = Session(title="Session 5", campaign_id=self.campaign1.id,
                                participants=[self.char_moderator, self.char_user], date=date(2001, 1, 1))
        self.session6 = Session(title="Session 6", campaign_id=self.campaign1.id,
                                participants=[self.char_moderator, self.char_user], date=date(2002, 1, 1))
        self.session7 = Session(title="Session 7", campaign_id=self.campaign1.id,
                                participants=[self.char_moderator, self.char_user], date=date(2003, 1, 1))
        self.session8 = Session(title="Session 8", campaign_id=self.campaign1.id,
                                participants=[self.char_moderator, self.char_user], date=date(2004, 1, 1))

        self.add_all([self.session5, self.session6, self.session7, self.session8])
        self.commit()
