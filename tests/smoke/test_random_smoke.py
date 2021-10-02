from flask import url_for
from tests import SmokeWrapper


class RandomTableSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_random_tables()

    def set_up_common_urls(self):
        self.common_urls = [self.random_table1.view_url(),
                            self.random_table1.edit_url(),
                            self.random_table1.roll_url(),
                            self.random_table1.roll_url(num_rolls=5),
                            self.random_table2.view_url(),
                            self.random_table2.edit_url(),
                            self.random_table2.roll_url(),
                            self.random_table2.roll_url(num_rolls=5),
                            self.random_table3.view_url(),
                            self.random_table3.edit_url(),
                            self.random_table3.roll_url(),
                            self.random_table3.roll_url(num_rolls=5)]
        self.common_endpoints = ["random.index", "random.table_create"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, self.random_table1.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table2.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table3.delete_url(), url=True, follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.random_table1.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table2.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table3.delete_url(), url=True, follow=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.random_table3.delete_url(), url=True, follow=True)


class RandomTableEntrySmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_random_tables()

    def set_up_common_urls(self):
        self.common_urls = [entry.view_url() for entry in self.random_table_entries]
        self.common_urls += [entry.edit_url() for entry in self.random_table_entries]
        self.common_urls += [url_for("random.table_entry_create", t_id=table.id, t_name=table.name)
                             for table in [self.random_table1, self.random_table2, self.random_table3]]
        self.common_endpoints = None

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, self.random_table_entries[0].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[1].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[2].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[3].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[4].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[5].delete_url(), url=True, follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.random_table_entries[0].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[1].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[2].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[3].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[4].delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.random_table_entries[5].delete_url(), url=True, follow=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.random_table_entries[3].delete_url(), url=True, follow=True)
