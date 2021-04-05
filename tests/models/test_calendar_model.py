from tests import BaseTestCase


class CalendarModelTest(BaseTestCase):
    """
    Nothing to test here currently
    """


class EpochModelTest(BaseTestCase):
    """
    Nothing to test here currently
    """


class MonthModelTest(BaseTestCase):
    """
    Nothing to test here currently
    """


class DayModelTest(BaseTestCase):
    """
    Nothing to test here currently
    """


class MoonModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_moons()

    def test_calc_phase(self, app, client):
        # cycle 'starts' with timestamp 1 (not 0)
        self.assertEqual(self.moons[0].calc_phase(1), 0.00)
        self.assertEqual(self.moons[0].calc_phase(2), 0.125)
        self.assertEqual(self.moons[0].calc_phase(3), 0.25)
        self.assertEqual(self.moons[0].calc_phase(4), 0.375)
        self.assertEqual(self.moons[0].calc_phase(5), 0.5)
        self.assertEqual(self.moons[0].calc_phase(6), 0.625)
        self.assertEqual(self.moons[0].calc_phase(7), 0.75)
        self.assertEqual(self.moons[0].calc_phase(8), 0.875)

        # test cycle
        for i in range(self.moons[0].phase_length):
            self.assertEqual(self.moons[0].calc_phase(i), self.moons[0].calc_phase(i + self.moons[0].phase_length),
                             f"moon cycle not matching for {i} and {i + self.moons[0].phase_length}")

        # test phase offset (moon[1] is 4 days offeset from moon[0])
        for i in range(8):
            self.assertEqual(self.moons[0].calc_phase(i), self.moons[1].calc_phase(i + 4),
                             f"moon phases not matching for {i} and {i + 4}")

        # TODO: some useful tests with non-nice values
        # aka moons[2]
        for i in range(self.moons[2].phase_length):
            self.assertEqual(self.moons[2].calc_phase(i), self.moons[2].calc_phase(i + self.moons[2].phase_length),
                             f"moon cycle not matching for {i} and {i + self.moons[2].phase_length}")

    def test_phase_name(self, app, client):
        # does not depend on the moon, as phase is parameter, not timestamp
        moon = self.moons[0]

        self.assertEqual(moon.phase_name(0), "Full Moon")
        self.assertEqual(moon.phase_name(0.1), "Waning gibbous")
        self.assertEqual(moon.phase_name(0.2), "Waning gibbous")
        self.assertEqual(moon.phase_name(0.25), "Third quarter")
        self.assertEqual(moon.phase_name(0.3), "Waning crescent")
        self.assertEqual(moon.phase_name(0.4), "Waning crescent")
        self.assertEqual(moon.phase_name(0.5), "New Moon")
        self.assertEqual(moon.phase_name(0.6), "Waxing crescent")
        self.assertEqual(moon.phase_name(0.7), "Waxing crescent")
        self.assertEqual(moon.phase_name(0.75), "First quarter")
        self.assertEqual(moon.phase_name(0.8), "Waxing gibbous")
        self.assertEqual(moon.phase_name(0.9), "Waxing gibbous")
        self.assertEqual(moon.phase_name(1), "Full Moon")

        # TODO: some testing with moon.delta
