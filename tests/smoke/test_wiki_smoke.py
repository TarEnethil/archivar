from app.wiki.models import WikiSetting
from flask import url_for
from tests import SmokeWrapper


class WikiSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_wiki()

        self.add(WikiSetting())
        self.commit()

    def set_up_common_urls(self):
        self.common_urls = [self.wiki_entry1.view_url(), self.wiki_entry1.edit_url(),
                            self.wiki_entry3.view_url(), self.wiki_entry3.edit_url(),
                            self.wiki_entry5.view_url(), self.wiki_entry5.edit_url(),
                            url_for("wiki.search_text", text="test"), url_for("wiki.search_tag", tag="test")]
        self.common_endpoints = ["wiki.create", "wiki.recent"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        # dont test entry1.delete, as it is id 1, which is not deletable
        self.assertHTTPOK(client, url_for("wiki.toggle_vis", id=self.wiki_entry1.id, name="x"), url=True, follow=True)

        self.assertHTTPOK(client, self.wiki_entry2.view_url(), url=True)
        self.assertHTTPOK(client, self.wiki_entry2.edit_url(), url=True)
        self.assertHTTPOK(client, url_for("wiki.toggle_vis", id=self.wiki_entry2.id, name="x"), url=True, follow=True)
        self.assertHTTPOK(client, self.wiki_entry2.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, "wiki.index", follow=True)
        self.assertHTTPOK(client, "wiki.settings")

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, url_for("wiki.toggle_vis", id=self.wiki_entry3.id, name="x"), url=True, follow=True)
        self.assertHTTPOK(client, self.wiki_entry3.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.wiki_entry4.view_url(), url=True)
        self.assertHTTPOK(client, self.wiki_entry4.edit_url(), url=True)
        self.assertHTTPOK(client, url_for("wiki.toggle_vis", id=self.wiki_entry4.id, name="x"), url=True, follow=True)
        self.assertHTTPOK(client, self.wiki_entry4.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, "wiki.index", follow=True)
        self.assertHTTPOK(client, "wiki.settings")

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, url_for("wiki.toggle_vis", id=self.wiki_entry5.id, name="x"), url=True, follow=True)
        self.assertHTTPOK(client, self.wiki_entry5.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.wiki_entry6.view_url(), url=True)
        self.assertHTTPOK(client, self.wiki_entry6.edit_url(), url=True)
        self.assertHTTPOK(client, url_for("wiki.toggle_vis", id=self.wiki_entry6.id, name="x"), url=True, follow=True)
        self.assertHTTPOK(client, self.wiki_entry6.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, "wiki.index", follow=True)
