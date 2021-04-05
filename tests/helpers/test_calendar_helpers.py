from tests import BaseTestCase
from app.calendar.models import CalendarSetting, Epoch, Month, Day
from flask import get_flashed_messages


class CalendarHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def test_own_sanity(self, app, client):
        """
        test that the static calendar in this test passes the sanity check
        """
        from app.calendar.helpers import calendar_sanity_check

        self.set_up_calendar()
        self.assertTrue(calendar_sanity_check())

    def test_get_next_epoch_order(self, app, client):
        from app.calendar.helpers import get_next_epoch_order

        self.assertEqual(get_next_epoch_order(), 1)

        self.add(Epoch(order=1))
        self.commit()

        self.assertEqual(get_next_epoch_order(), 2)

        e2 = Epoch(order=2)
        self.add(e2)
        self.commit()

        self.assertEqual(get_next_epoch_order(), 3)

        self.add(Epoch(order=3))
        self.rem(e2)
        self.commit()

        self.assertEqual(get_next_epoch_order(), 4)

    def test_get_next_month_order(self, app, client):
        from app.calendar.helpers import get_next_month_order

        self.assertEqual(get_next_month_order(), 1)

        self.add(Month(order=1))
        self.commit()

        self.assertEqual(get_next_month_order(), 2)

        m2 = Month(order=2)
        self.add(m2)
        self.commit()

        self.assertEqual(get_next_month_order(), 3)

        self.add(Month(order=3))
        self.rem(m2)
        self.commit()

        self.assertEqual(get_next_month_order(), 4)

    def test_get_next_day_order(self, app, client):
        from app.calendar.helpers import get_next_day_order

        self.assertEqual(get_next_day_order(), 1)

        self.add(Day(order=1))
        self.commit()

        self.assertEqual(get_next_day_order(), 2)

        d2 = Day(order=2)
        self.add(d2)
        self.commit()

        self.assertEqual(get_next_day_order(), 3)

        self.add(Day(order=3))
        self.rem(d2)
        self.commit()

        self.assertEqual(get_next_day_order(), 4)

    def test_calendar_sanity_check(self, app, client):
        from app.calendar.helpers import calendar_sanity_check

        # need settings with id 1 to exist (part of install)
        settings = CalendarSetting(finalized=True)
        self.add(settings)
        self.commit()

        # fail-case: calendar is already finalized
        client.get("/")
        with client.session_transaction():
            self.assertFalse(calendar_sanity_check())
            self.assertTrue("already finalized" in get_flashed_messages()[0])

        settings.finalized = False
        self.commit()

        # fail-case: calendar has no epochs
        client.get("/")
        with client.session_transaction():
            self.assertFalse(calendar_sanity_check())
            self.assertTrue("needs at least one epoch" in get_flashed_messages()[0])

        self.set_up_epochs()
        self.epochs[2].years = 100
        self.commit()

        # fail-case: current epoch has years != 0
        client.get("/")
        with client.session_transaction():
            self.assertFalse(calendar_sanity_check())
            self.assertTrue("needs a duration of 0" in get_flashed_messages()[0])

        self.epochs[2].years = 0
        self.epochs[1].years = 0
        self.commit()

        # fail-case: not-current epoch has duration 0
        client.get("/")
        with client.session_transaction():
            self.assertFalse(calendar_sanity_check())
            self.assertTrue("need a duration > 0" in get_flashed_messages()[0])

        self.epochs[1].years = 200
        self.commit()

        # fail-case: calendar has no months
        client.get("/")
        with client.session_transaction():
            self.assertFalse(calendar_sanity_check())
            self.assertTrue("needs at least one month" in get_flashed_messages()[0])

        self.set_up_months()

        # fail-case: calendar has no days
        client.get("/")
        with client.session_transaction():
            self.assertFalse(calendar_sanity_check())
            self.assertTrue("needs at least one day" in get_flashed_messages()[0])

        self.set_up_days()

        # success case
        client.get("/")
        with client.session_transaction():
            self.assertTrue(calendar_sanity_check())

    def test_gen_calendar_preview_data(self, app, client):
        from app.calendar.helpers import gen_calendar_preview_data

        self.set_up_calendar()

        info = gen_calendar_preview_data()

        self.assertEqual(len(info["epochs"]), len(self.epochs))
        self.assertEqual(len(info["months"]), len(self.months))
        self.assertEqual(len(info["days"]), len(self.days))
        self.assertEqual(len(info["moons"]), len(self.moons))
        self.assertEqual(info["days_per_week"], len(self.days))
        self.assertEqual(info["days_per_year"], 100)
        self.assertEqual(info["months_per_year"], len(self.months))

        # roll back non-commited changes
        self.db.session.rollback()

        # implicit commit=False means this should not have been commited
        for i in range(len(self.epochs)):
            self.assertEqual(self.epochs[i].years_before, 0)

        # implicit commit=False means this should not have been commited
        for i in range(len(self.months)):
            self.assertEqual(self.months[i].days_before, 0)

        gen_calendar_preview_data(commit=True)

        # data should be there even after rollback (they were commited)
        self.db.session.rollback()

        self.assertEqual(self.epochs[0].years_before, 0)
        self.assertEqual(self.epochs[1].years_before, 100)
        self.assertEqual(self.epochs[2].years_before, 300)

        self.assertEqual(self.months[0].days_before, 0)
        self.assertEqual(self.months[1].days_before, 10)
        self.assertEqual(self.months[2].days_before, 30)
        self.assertEqual(self.months[3].days_before, 60)

    def test_gen_calendar_stats(self, app, client):
        from app.calendar.helpers import gen_calendar_stats

        self.set_up_calendar(finalized=True)

        info = gen_calendar_stats()

        self.assertEqual(len(info["epochs"]), len(self.epochs))
        self.assertEqual(len(info["months"]), len(self.months))
        self.assertEqual(len(info["days"]), len(self.days))
        self.assertEqual(len(info["moons"]), len(self.moons))
        self.assertEqual(info["days_per_week"], len(self.days))
        self.assertEqual(info["days_per_year"], 100)
        self.assertEqual(info["months_per_year"], len(self.months))

        # TODO: maybe revisit after adding event categories to self
        self.assertEqual(len(info["categories"]), 0)

    def test_gen_epoch_choices(self, app, client):
        from app.calendar.helpers import gen_epoch_choices

        self.assertEqual(len(gen_epoch_choices()), 0)

        self.set_up_epochs()

        self.assertEqual(len(gen_epoch_choices()), 3)

    def test_gen_month_choices(self, app, client):
        from app.calendar.helpers import gen_month_choices

        self.assertEqual(len(gen_month_choices()), 0)

        self.set_up_months()

        self.assertEqual(len(gen_month_choices()), 4)

    def test_gen_day_choices(self, app, client):
        from app.calendar.helpers import gen_day_choices

        with self.assertRaises(LookupError) as cm:
            gen_day_choices(1)

        self.assertTrue("No month" in str(cm.exception))

        self.set_up_months()

        self.assertEqual(len(gen_day_choices(self.months[0].id)), self.months[0].days)
        self.assertEqual(len(gen_day_choices(self.months[1].id)), self.months[1].days)
        self.assertEqual(len(gen_day_choices(self.months[2].id)), self.months[2].days)
        self.assertEqual(len(gen_day_choices(self.months[3].id)), self.months[3].days)

    def test_get_epochs(self, app, client):
        from app.calendar.helpers import get_epochs

        self.assertEqual(len(get_epochs()), 0)

        self.set_up_epochs()

        self.assertEqual(len(get_epochs()), 3)

    def test_get_years_in_epoch(self, app, client):
        from app.calendar.helpers import get_years_in_epoch

        self.set_up_users()
        self.set_up_calendar(finalized=True)
        self.set_up_events()

        self.login(client, self.admin)
        years = get_years_in_epoch(self.epochs[0].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 3)
        self.assertTrue(1 in years)
        self.assertTrue(2 in years)
        self.assertTrue(3 in years)

        years = get_years_in_epoch(self.epochs[1].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 1)
        self.assertTrue(102 in years)

        years = get_years_in_epoch(self.epochs[2].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 0)

        self.login(client, self.moderator)
        years = get_years_in_epoch(self.epochs[0].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 2)
        self.assertTrue(1 in years)
        self.assertTrue(3 in years)

        years = get_years_in_epoch(self.epochs[1].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 2)
        self.assertTrue(101 in years)
        self.assertTrue(102 in years)

        years = get_years_in_epoch(self.epochs[2].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 0)

        self.login(client, self.user)
        years = get_years_in_epoch(self.epochs[0].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 2)
        self.assertTrue(1 in years)
        self.assertTrue(3 in years)

        years = get_years_in_epoch(self.epochs[1].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 1)
        self.assertTrue(102 in years)

        years = get_years_in_epoch(self.epochs[2].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 1)
        self.assertTrue(301 in years)

        self.login(client, self.user2)
        years = get_years_in_epoch(self.epochs[0].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 2)
        self.assertTrue(1 in years)
        self.assertTrue(3 in years)

        years = get_years_in_epoch(self.epochs[1].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 1)
        self.assertTrue(102 in years)

        years = get_years_in_epoch(self.epochs[2].id)
        years = [y[0] for y in years]
        self.assertEqual(len(years), 0)
