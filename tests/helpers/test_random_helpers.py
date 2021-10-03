from tests import BaseTestCase


class RandomHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def test_is_valid_dice_string(self, app, client):
        from app.random.helpers import is_valid_dice_string

        self.assertTrue(is_valid_dice_string("1d6"))
        self.assertTrue(is_valid_dice_string("d6"))
        self.assertTrue(is_valid_dice_string("3d6+7"))
        self.assertTrue(is_valid_dice_string("1d6+3d6+7"))
        self.assertTrue(is_valid_dice_string("3d6+7 [comment]"))
        self.assertTrue(is_valid_dice_string("3d6pl1"))
        self.assertTrue(is_valid_dice_string("3d6kh1"))
        self.assertTrue(is_valid_dice_string("3"))

        self.assertFalse(is_valid_dice_string("3d"))
        self.assertFalse(is_valid_dice_string(""))
        self.assertFalse(is_valid_dice_string("hello world"))
        self.assertFalse(is_valid_dice_string("[hello world]"))
