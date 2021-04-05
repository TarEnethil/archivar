from tests import BaseTestCase


class UserHelperTest(BaseTestCase):
    """
    Not the most useful tests right now, but works for testing how testing works.
    """
    def test_gen_role_choices(self, app, client):
        from app.helpers import Role
        from app.user.helpers import gen_role_choices

        self.assertEqual(len(gen_role_choices()), len(Role))

    def test_date_string_choices(self, app, client):
        from app.user.helpers import gen_date_string_choices

        self.assertEqual(len(gen_date_string_choices()), 9)
