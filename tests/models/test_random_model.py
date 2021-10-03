from tests import BaseTestCase


class RandomTableModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_random_tables()

    def test_get_total_weight(self, app, client):
        self.assertEqual(3, self.random_table1.get_total_weight())
        self.assertEqual(111, self.random_table2.get_total_weight())
        self.assertEqual(0, self.random_table3.get_total_weight())

    def test_roll(self, app, client):
        roll = self.random_table1.roll(3)
        self.assertEqual(3, len(roll))
        self.assertTrue(roll[0] in self.random_table1.entries)
        self.assertTrue(roll[1] in self.random_table1.entries)
        self.assertTrue(roll[2] in self.random_table1.entries)

        self.assertIsNone(self.random_table3.roll(3))

    def test_roll_once(self, app, client):
        roll = self.random_table1.roll_once()
        self.assertTrue(roll in self.random_table1.entries)

        self.assertIsNone(self.random_table3.roll_once())


class RandomTableEntryModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_random_tables()

    def test_get_chance(self, app, client):
        self.assertEqual("33.33%", self.random_table_entries[0].get_chance())
        self.assertEqual("66.67%", self.random_table_entries[1].get_chance())
        self.assertEqual("2.70%", self.random_table_entries[2].get_chance())
        self.assertEqual("2.70%", self.random_table_entries[3].get_chance())
        self.assertEqual("4.50%", self.random_table_entries[4].get_chance())
        self.assertEqual("90.09%", self.random_table_entries[5].get_chance())


class DiceSetModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_random_dice()

    def test_roll(self, app, client):
        roll = self.dice_set1.roll(3)
        self.assertEqual(3, len(roll))
        for i in range(0, 3):
            self.assertGreaterEqual(roll[i].total, 1)
            self.assertLessEqual(roll[i].total, 6)

    def test_roll_once(self, app, client):
        roll = self.dice_set1.roll_once()
        self.assertGreaterEqual(roll.total, 1)
        self.assertLessEqual(roll.total, 6)
