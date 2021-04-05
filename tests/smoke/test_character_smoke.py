from flask import url_for
from tests import SmokeWrapper


class CharacterSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_characters()

    def set_up_common_urls(self):
        self.common_urls = [self.char_admin.view_url(), self.char_moderator.view_url(), self.char_user.view_url()]
        self.common_endpoints = ["character.create", "character.list"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, self.char_admin.edit_url(), url=True)
        self.assertHTTPOK(client, self.char_admin_priv.edit_url(), url=True)

        self.assertHTTPOK(client, self.char_admin.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.char_admin_priv.delete_url(), url=True, follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.char_moderator.edit_url(), url=True)
        self.assertHTTPOK(client, self.char_moderator_priv.edit_url(), url=True)

        self.assertHTTPOK(client, self.char_moderator.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.char_moderator_priv.delete_url(), url=True, follow=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.char_user.edit_url(), url=True)
        self.assertHTTPOK(client, self.char_user_priv.edit_url(), url=True)

        self.assertHTTPOK(client, self.char_user.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.char_user_priv.delete_url(), url=True, follow=True)


class JournalSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_characters()
        self.set_up_journals()

    def set_up_common_urls(self):
        self.common_urls = [self.journal_admin.view_url(),
                            self.journal_moderator.view_url(),
                            self.journal_user.view_url(),
                            url_for("character.journal_list", c_id=self.char_admin.id,
                                    c_name=self.char_admin.name),
                            url_for("character.journal_list", c_id=self.char_moderator.id,
                                    c_name=self.char_moderator.name),
                            url_for("character.journal_list", c_id=self.char_user.id,
                                    c_name=self.char_user.name)]
        self.common_endpoints = None

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, url_for("character.journal_create", c_id=self.char_admin.id,
                                          c_name=self.char_admin.name), url=True)
        self.assertHTTPOK(client, url_for("character.journal_create", c_id=self.char_admin_priv.id,
                                          c_name=self.char_admin_priv.name), url=True)

        self.assertHTTPOK(client, self.journal_admin.edit_url(), url=True)
        self.assertHTTPOK(client, self.journal_admin_priv.edit_url(), url=True)

        self.assertHTTPOK(client, self.journal_admin.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.journal_admin_priv.delete_url(), url=True, follow=True)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, url_for("character.journal_create", c_id=self.char_moderator.id,
                                          c_name=self.char_moderator.name), url=True)
        self.assertHTTPOK(client, url_for("character.journal_create", c_id=self.char_moderator_priv.id,
                                          c_name=self.char_moderator_priv.name), url=True)

        self.assertHTTPOK(client, self.journal_moderator.edit_url(), url=True)
        self.assertHTTPOK(client, self.journal_moderator_priv.edit_url(), url=True)

        self.assertHTTPOK(client, self.journal_moderator.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.journal_moderator_priv.delete_url(), url=True, follow=True)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, url_for("character.journal_create", c_id=self.char_user.id,
                                          c_name=self.char_user.name), url=True)
        self.assertHTTPOK(client, url_for("character.journal_create", c_id=self.char_user_priv.id,
                                          c_name=self.char_user_priv.name), url=True)

        self.assertHTTPOK(client, self.journal_user.edit_url(), url=True)
        self.assertHTTPOK(client, self.journal_user_priv.edit_url(), url=True)

        self.assertHTTPOK(client, self.journal_user.delete_url(), url=True, follow=True)
        self.assertHTTPOK(client, self.journal_user_priv.delete_url(), url=True, follow=True)
