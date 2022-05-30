from tests import BaseTestCase


class EventModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_calendar(finalized=True)
        self.set_up_events()

    def test_format_date(self, app, client):
        """
        implicitly tested with start_date
        """
        pass

    def test_start_date(self, app, client):
        """
        TODO: possibly test with with_link param
        """
        self.assertEqual(self.event1.start_date(use_abbr=False), "1. Month 1 1, Epoch 1")
        self.assertEqual(self.event2.start_date(use_abbr=False), "2. Month 2 2, Epoch 1")
        self.assertEqual(self.event3.start_date(use_abbr=False), "3. Month 3 3, Epoch 1")
        self.assertEqual(self.event4.start_date(use_abbr=False), "10. Month 4 101, Epoch 2")
        self.assertEqual(self.event5.start_date(use_abbr=False), "11. Month 4 102, Epoch 2")
        self.assertEqual(self.event6.start_date(use_abbr=False), "4. Month 3 301, Epoch 3")

        # test permutations of params
        self.assertEqual(self.event4.start_date(use_abbr=True), "10. M4 101, E2")
        self.assertEqual(self.event4.start_date(use_abbr=True, use_epoch=False), "10. M4 101")
        self.assertEqual(self.event4.start_date(use_abbr=False, use_epoch=False), "10. Month 4 101")
        self.assertEqual(self.event4.start_date(use_abbr=False, use_epoch=False, use_year=False), "10. Month 4")
        self.assertEqual(self.event4.start_date(use_abbr=True, use_epoch=False, with_weekday=True), "D5, 10. M4 101")
        self.assertEqual(self.event4.start_date(use_abbr=False, use_epoch=False, with_weekday=True),
                         "Day 5, 10. Month 4 101")
        self.assertEqual(self.event4.start_date(use_abbr=False, use_epoch=False, use_year=False, with_weekday=True),
                         "Day 5, 10. Month 4")

        # tests with no abbreviations available
        self.assertEqual(self.event6.start_date(use_abbr=True), "4. Month 3 301, Epoch 3")
        self.assertEqual(self.event6.start_date(use_abbr=True, use_epoch=False), "4. Month 3 301")
        self.assertEqual(self.event6.start_date(use_abbr=True, use_epoch=False, with_weekday=True),
                         "Day 4, 4. Month 3 301")
        self.assertEqual(self.event6.start_date(use_abbr=True, use_epoch=False, use_year=False, with_weekday=True),
                         "Day 4, 4. Month 3")

    def test_end_date(self, app, client):
        # TODO: test end dates, take care for borders of months, years and epochs
        self.assertEqual(self.event1.end_date(use_abbr=False), "2. Month 1 1, Epoch 1")
        self.assertEqual(self.event2.end_date(use_abbr=False), "4. Month 2 2, Epoch 1")
        self.assertEqual(self.event3.end_date(use_abbr=False), "6. Month 3 3, Epoch 1")
        self.assertEqual(self.event4.end_date(use_abbr=False), "11. Month 4 101, Epoch 2")
        self.assertEqual(self.event5.end_date(use_abbr=False), "12. Month 4 102, Epoch 2")
        self.assertEqual(self.event6.end_date(use_abbr=False), "5. Month 3 301, Epoch 3")

        # test permutations of params
        self.assertEqual(self.event4.end_date(use_abbr=True), "11. M4 101, E2")
        self.assertEqual(self.event4.end_date(use_abbr=True, use_epoch=False), "11. M4 101")
        self.assertEqual(self.event4.end_date(use_abbr=False, use_epoch=False), "11. Month 4 101")
        self.assertEqual(self.event4.end_date(use_abbr=False, use_epoch=False, use_year=False), "11. Month 4")
        self.assertEqual(self.event4.end_date(use_abbr=True, use_epoch=False, with_weekday=True), "D1, 11. M4 101")
        self.assertEqual(self.event4.end_date(use_abbr=False, use_epoch=False, with_weekday=True),
                         "Day 1, 11. Month 4 101")
        self.assertEqual(self.event4.end_date(use_abbr=False, use_epoch=False, use_year=False, with_weekday=True),
                         "Day 1, 11. Month 4")

        # set event6.day so that end-date falls on Day 4 (which has no abbreviation)
        self.event6.day = 3
        self.commit()
        from app.event.helpers import update_timestamp
        update_timestamp(self.event6.id)

        # tests with no abbreviations available
        self.assertEqual(self.event6.end_date(use_abbr=True), "4. Month 3 301, Epoch 3")
        self.assertEqual(self.event6.end_date(use_abbr=True, use_epoch=False), "4. Month 3 301")
        self.assertEqual(self.event6.end_date(use_abbr=True, use_epoch=False, with_weekday=True),
                         "Day 4, 4. Month 3 301")
        self.assertEqual(self.event6.end_date(use_abbr=True, use_epoch=False, use_year=False, with_weekday=True),
                         "Day 4, 4. Month 3")

        # test transitions between months, years and epochs
        from app.event.models import Event
        # event ends in next month (10 days for first month + 5 days)
        event_month = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=1, duration=15)
        # event ends in next year (100 days_per_year + 5 days)
        event_year = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=1, duration=105)
        # event ends in next year and next month (100 days_per_year + 10 days first month + 5 days)
        event_month_year = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=1, duration=115)
        # event ends in the next epoch (100 days_per_year * 100 years + 5 days)
        event_epoch = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=1, duration=100*100+5)
        # event ends in the next epoch and next month (100 days_per_year * 100 years + 10 days first month + 5 days)
        event_month_epoch = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=1,
                                  duration=100*100+15)
        # event ends in next epoch, month and year (100 days_per_year * 101 years + 10 days first month + 5 days)
        event_month_year_epoch = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=1,
                                       duration=100*101+15)
        # event that starts in epoch 1 and ends in epoch 3, skips another year and a month as well
        event_skip_two_epochs = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=1,
                                      duration=100*301+15)

        # re-test for bug #119, let an event end at the last day of a month
        event_last_of_month = Event(epoch_id=self.epochs[0].id, year=1, month_id=self.months[0].id, day=8, duration=2)

        self.add_all([event_month, event_year, event_month_year, event_epoch,
                      event_month_epoch, event_month_year_epoch, event_skip_two_epochs,
                      event_last_of_month])
        self.commit()

        update_timestamp(event_month.id)
        update_timestamp(event_year.id)
        update_timestamp(event_month_year.id)
        update_timestamp(event_epoch.id)
        update_timestamp(event_month_epoch.id)
        update_timestamp(event_month_year_epoch.id)
        update_timestamp(event_skip_two_epochs.id)
        update_timestamp(event_last_of_month.id)

        self.assertEqual(event_month.end_date(use_abbr=False), "6. Month 2 1, Epoch 1")
        self.assertEqual(event_year.end_date(use_abbr=False), "6. Month 1 2, Epoch 1")
        self.assertEqual(event_month_year.end_date(use_abbr=False), "6. Month 2 2, Epoch 1")
        self.assertEqual(event_epoch.end_date(use_abbr=False), "6. Month 1 1, Epoch 2")
        self.assertEqual(event_month_epoch.end_date(use_abbr=False), "6. Month 2 1, Epoch 2")
        self.assertEqual(event_month_year_epoch.end_date(use_abbr=False), "6. Month 2 2, Epoch 2")
        self.assertEqual(event_skip_two_epochs.end_date(use_abbr=False), "6. Month 2 2, Epoch 3")

        # bug #119, this would show "0. Month 2" before
        self.assertEqual(event_last_of_month.end_date(use_abbr=False), "10. Month 1 1, Epoch 1")

    def test_day_of_the_week(self, app, client):
        # with static timestamp
        self.assertEqual(self.event1.day_of_the_week(1), self.days[0].name)

        # with self
        self.assertEqual(self.event1.day_of_the_week(), self.days[0].name)
        self.assertEqual(self.event2.day_of_the_week(), self.days[1].name)
        self.assertEqual(self.event3.day_of_the_week(), self.days[2].name)
        self.assertEqual(self.event4.day_of_the_week(), self.days[4].name)
        self.assertEqual(self.event5.day_of_the_week(), self.days[0].name)
        self.assertEqual(self.event6.day_of_the_week(), self.days[3].name)

        # with abbreviation (event6 has no abbreviation)
        self.assertEqual(self.event1.day_of_the_week(use_abbr=True), self.days[0].abbreviation)
        self.assertEqual(self.event2.day_of_the_week(use_abbr=True), self.days[1].abbreviation)
        self.assertEqual(self.event3.day_of_the_week(use_abbr=True), self.days[2].abbreviation)
        self.assertEqual(self.event4.day_of_the_week(use_abbr=True), self.days[4].abbreviation)
        self.assertEqual(self.event5.day_of_the_week(use_abbr=True), self.days[0].abbreviation)
        self.assertEqual(self.event6.day_of_the_week(), self.days[3].name)

    def test_permissions(self, app, client):
        ########
        # Admin
        ########
        # Owns Media 1 and 2
        self.login(client, self.admin)
        self.assertTrue(self.event1.is_viewable_by_user())
        self.assertTrue(self.event1.is_editable_by_user())
        self.assertTrue(self.event1.is_hideable_by_user())
        self.assertTrue(self.event1.is_deletable_by_user())

        self.assertTrue(self.event2.is_viewable_by_user())
        self.assertTrue(self.event2.is_editable_by_user())
        self.assertTrue(self.event2.is_hideable_by_user())
        self.assertTrue(self.event2.is_deletable_by_user())

        self.assertTrue(self.event3.is_viewable_by_user())
        self.assertTrue(self.event3.is_editable_by_user())
        self.assertFalse(self.event3.is_hideable_by_user())
        self.assertTrue(self.event3.is_deletable_by_user())

        self.assertFalse(self.event4.is_viewable_by_user())
        self.assertFalse(self.event4.is_editable_by_user())
        self.assertFalse(self.event4.is_hideable_by_user())
        self.assertFalse(self.event4.is_deletable_by_user())

        self.assertTrue(self.event5.is_viewable_by_user())
        self.assertTrue(self.event5.is_editable_by_user())
        self.assertFalse(self.event5.is_hideable_by_user())
        self.assertTrue(self.event5.is_deletable_by_user())

        self.assertFalse(self.event6.is_viewable_by_user())
        self.assertFalse(self.event6.is_editable_by_user())
        self.assertFalse(self.event6.is_hideable_by_user())
        self.assertFalse(self.event6.is_deletable_by_user())

        ########
        # Moderator
        ########
        # Owns Media 3 and 4
        self.login(client, self.moderator)
        self.assertTrue(self.event1.is_viewable_by_user())
        self.assertTrue(self.event1.is_editable_by_user())
        self.assertFalse(self.event1.is_hideable_by_user())
        self.assertTrue(self.event1.is_deletable_by_user())

        self.assertFalse(self.event2.is_viewable_by_user())
        self.assertFalse(self.event2.is_editable_by_user())
        self.assertFalse(self.event2.is_hideable_by_user())
        self.assertFalse(self.event2.is_deletable_by_user())

        self.assertTrue(self.event3.is_viewable_by_user())
        self.assertTrue(self.event3.is_editable_by_user())
        self.assertTrue(self.event3.is_hideable_by_user())
        self.assertTrue(self.event3.is_deletable_by_user())

        self.assertTrue(self.event4.is_viewable_by_user())
        self.assertTrue(self.event4.is_editable_by_user())
        self.assertTrue(self.event4.is_hideable_by_user())
        self.assertTrue(self.event4.is_deletable_by_user())

        self.assertTrue(self.event5.is_viewable_by_user())
        self.assertTrue(self.event5.is_editable_by_user())
        self.assertFalse(self.event5.is_hideable_by_user())
        self.assertTrue(self.event5.is_deletable_by_user())

        self.assertFalse(self.event6.is_viewable_by_user())
        self.assertFalse(self.event6.is_editable_by_user())
        self.assertFalse(self.event6.is_hideable_by_user())
        self.assertFalse(self.event6.is_deletable_by_user())

        ########
        # User
        ########
        # Owns Media 5 and 6
        self.login(client, self.user)
        self.assertTrue(self.event1.is_viewable_by_user())
        self.assertTrue(self.event1.is_editable_by_user())
        self.assertFalse(self.event1.is_hideable_by_user())
        self.assertFalse(self.event1.is_deletable_by_user())

        self.assertFalse(self.event2.is_viewable_by_user())
        self.assertFalse(self.event2.is_editable_by_user())
        self.assertFalse(self.event2.is_hideable_by_user())
        self.assertFalse(self.event2.is_deletable_by_user())

        self.assertTrue(self.event3.is_viewable_by_user())
        self.assertTrue(self.event3.is_editable_by_user())
        self.assertFalse(self.event3.is_hideable_by_user())
        self.assertFalse(self.event3.is_deletable_by_user())

        self.assertFalse(self.event4.is_viewable_by_user())
        self.assertFalse(self.event4.is_editable_by_user())
        self.assertFalse(self.event4.is_hideable_by_user())
        self.assertFalse(self.event4.is_deletable_by_user())

        self.assertTrue(self.event5.is_viewable_by_user())
        self.assertTrue(self.event5.is_editable_by_user())
        self.assertTrue(self.event5.is_hideable_by_user())
        self.assertTrue(self.event5.is_deletable_by_user())

        self.assertTrue(self.event6.is_viewable_by_user())
        self.assertTrue(self.event6.is_editable_by_user())
        self.assertTrue(self.event6.is_hideable_by_user())
        self.assertTrue(self.event6.is_deletable_by_user())

        ########
        # User2
        ########
        # Does not own any event
        self.login(client, self.user2)
        self.assertTrue(self.event1.is_viewable_by_user())
        self.assertTrue(self.event1.is_editable_by_user())
        self.assertFalse(self.event1.is_hideable_by_user())
        self.assertFalse(self.event1.is_deletable_by_user())

        self.assertFalse(self.event2.is_viewable_by_user())
        self.assertFalse(self.event2.is_editable_by_user())
        self.assertFalse(self.event2.is_hideable_by_user())
        self.assertFalse(self.event2.is_deletable_by_user())

        self.assertTrue(self.event3.is_viewable_by_user())
        self.assertTrue(self.event3.is_editable_by_user())
        self.assertFalse(self.event3.is_hideable_by_user())
        self.assertFalse(self.event3.is_deletable_by_user())

        self.assertFalse(self.event4.is_viewable_by_user())
        self.assertFalse(self.event4.is_editable_by_user())
        self.assertFalse(self.event4.is_hideable_by_user())
        self.assertFalse(self.event4.is_deletable_by_user())

        self.assertTrue(self.event5.is_viewable_by_user())
        self.assertTrue(self.event5.is_editable_by_user())
        self.assertFalse(self.event5.is_hideable_by_user())
        self.assertFalse(self.event5.is_deletable_by_user())

        self.assertFalse(self.event6.is_viewable_by_user())
        self.assertFalse(self.event6.is_editable_by_user())
        self.assertFalse(self.event6.is_hideable_by_user())
        self.assertFalse(self.event6.is_deletable_by_user())


class EventCategoryModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_calendar()
        self.set_up_events()

    def test_get_events(self, app, client):
        self.login(client, self.admin)
        events = self.event_cat1.get_events()
        self.assertEqual(len(events), 3)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event2 in events)
        self.assertTrue(self.event3 in events)

        events = self.event_cat2.get_events()
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event5 in events)

        self.assertEqual(len(self.event_cat3.get_events()), 0)

        self.login(client, self.moderator)
        events = self.event_cat1.get_events()
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)

        events = self.event_cat2.get_events()
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event4 in events)
        self.assertTrue(self.event5 in events)

        self.assertEqual(len(self.event_cat3.get_events()), 0)

        self.login(client, self.user)
        events = self.event_cat1.get_events()
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)

        events = self.event_cat2.get_events()
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event5 in events)

        events = self.event_cat3.get_events()
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event6 in events)

        self.login(client, self.user2)
        events = self.event_cat1.get_events()
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)

        events = self.event_cat2.get_events()
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event5 in events)

        self.assertEqual(len(self.event_cat3.get_events()), 0)
