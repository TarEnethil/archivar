from tests import BaseTestCase


class EventHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_calendar(finalized=True)
        self.set_up_events(timestamps=False)

    def test_gen_event_category_choices(self, app, client):
        from app.event.helpers import gen_event_category_choices

        self.assertEqual(len(gen_event_category_choices()), 3)

    def test_get_event_categories(self, app, client):
        from app.event.helpers import get_event_categories

        self.assertEqual(len(get_event_categories()), 3)

    def test_update_timestamp(self, app, client):
        from app.event.helpers import update_timestamp

        update_timestamp(self.event1.id)
        update_timestamp(self.event2.id)
        update_timestamp(self.event3.id)
        update_timestamp(self.event4.id)
        update_timestamp(self.event5.id)
        update_timestamp(self.event6.id)

        # rhs calculated by hand
        self.assertEqual(self.event1.timestamp, 1)
        self.assertEqual(self.event2.timestamp, 100 + 10 + 2)
        self.assertEqual(self.event3.timestamp, 2*100 + 10 + 20 + 3)
        self.assertEqual(self.event4.timestamp, 100*100 + 100*100 + 10 + 20 + 30 + 10)
        self.assertEqual(self.event5.timestamp, 100*100 + 101*100 + 10 + 20 + 30 + 11)
        self.assertEqual(self.event6.timestamp, 200*100 + 100*100 + 300*100 + 10 + 20 + 4)

        # test noop / no raise when using invalid id
        update_timestamp(100)

    def test_get_events(self, app, client):
        from app.event.helpers import get_events

        # test admin and the filters
        self.login(client, self.admin)
        events = get_events()
        self.assertEqual(len(events), 4)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event2 in events)
        self.assertTrue(self.event3 in events)
        self.assertTrue(self.event5 in events)

        events = get_events(filter_epoch=self.epochs[0].id)
        self.assertEqual(len(events), 3)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event2 in events)
        self.assertTrue(self.event3 in events)

        events = get_events(filter_epoch=self.epochs[0].id, filter_year=1)
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event1 in events)

        # no visible events in epoch 2 for admin
        self.assertEqual(len(get_events(filter_epoch=self.epochs[2].id)), 0)

        # no events in epoch 1, year 5
        self.assertEqual(len(get_events(filter_epoch=self.epochs[0].id, filter_year=5)), 0)

        # just check visibility from here on, filters are already tested
        self.login(client, self.moderator)
        events = get_events()
        self.assertEqual(len(events), 4)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)
        self.assertTrue(self.event4 in events)
        self.assertTrue(self.event5 in events)

        self.login(client, self.user)
        events = get_events()
        self.assertEqual(len(events), 4)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)
        self.assertTrue(self.event5 in events)
        self.assertTrue(self.event6 in events)

        self.login(client, self.user2)
        events = get_events()
        self.assertEqual(len(events), 3)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)
        self.assertTrue(self.event5 in events)

    def test_get_events_by_category(self, app, client):
        from app.event.helpers import get_events_by_category

        self.login(client, self.admin)
        events = get_events_by_category(self.event_cat1.id)
        self.assertEqual(len(events), 3)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event2 in events)
        self.assertTrue(self.event3 in events)

        events = get_events_by_category(self.event_cat2.id)
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event5 in events)

        events = get_events_by_category(self.event_cat3.id)
        self.assertEqual(len(events), 0)

        self.login(client, self.moderator)
        events = get_events_by_category(self.event_cat1.id)
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)

        events = get_events_by_category(self.event_cat2.id)
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event4 in events)
        self.assertTrue(self.event5 in events)

        events = get_events_by_category(self.event_cat3.id)
        self.assertEqual(len(events), 0)

        self.login(client, self.user)
        events = get_events_by_category(self.event_cat1.id)
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)

        events = get_events_by_category(self.event_cat2.id)
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event5 in events)

        events = get_events_by_category(self.event_cat3.id)
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event6 in events)

        self.login(client, self.user2)
        events = get_events_by_category(self.event_cat1.id)
        self.assertEqual(len(events), 2)
        self.assertTrue(self.event1 in events)
        self.assertTrue(self.event3 in events)

        events = get_events_by_category(self.event_cat2.id)
        self.assertEqual(len(events), 1)
        self.assertTrue(self.event5 in events)

        events = get_events_by_category(self.event_cat3.id)
        self.assertEqual(len(events), 0)
