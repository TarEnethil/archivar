from tests import BaseTestCase


class WikiHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_wiki()

    def test_gen_wiki_entry_choices(self, app, client):
        from app.wiki.helpers import gen_wiki_entry_choices

        self.login(client, self.admin)
        choices = gen_wiki_entry_choices()
        self.assertEqual(len(choices), 3)  # no link, main category, cat 1
        self.assertEqual(len(choices[1][1]), 1)
        self.assertEqual(len(choices[2][1]), 3)

        # test ensure
        choices = gen_wiki_entry_choices(self.wiki_entry4)
        self.assertEqual(len(choices), 4)  # no link, main category, cat 1, cat 2
        self.assertEqual(len(choices[1][1]), 1)
        self.assertEqual(len(choices[2][1]), 3)
        self.assertEqual(len(choices[3][1]), 1)

        self.login(client, self.moderator)
        choices = gen_wiki_entry_choices()
        self.assertEqual(len(choices), 4)  # no link, main category, cat 1, cat 2
        self.assertEqual(len(choices[1][1]), 1)
        self.assertEqual(len(choices[2][1]), 2)
        self.assertEqual(len(choices[3][1]), 1)

        self.login(client, self.user)
        choices = gen_wiki_entry_choices()
        self.assertEqual(len(choices), 3)  # no link, main category, cat 1
        self.assertEqual(len(choices[1][1]), 2)
        self.assertEqual(len(choices[2][1]), 2)

        self.login(client, self.user2)
        choices = gen_wiki_entry_choices()
        self.assertEqual(len(choices), 3)  # no link, main category, cat 1
        self.assertEqual(len(choices[1][1]), 1)
        self.assertEqual(len(choices[2][1]), 2)

    def test_gen_wiki_category_choices(self, app, client):
        from app.wiki.helpers import gen_wiki_category_choices

        self.login(client, self.admin)
        categories = gen_wiki_category_choices()
        self.assertEqual(len(categories), 2)  # Choose + Cat 1
        self.assertEqual(categories[1][1], "Cat 1")

        self.login(client, self.moderator)
        categories = gen_wiki_category_choices()
        self.assertEqual(len(categories), 3)
        self.assertEqual(categories[1][1], "Cat 1")
        self.assertEqual(categories[2][1], "Cat 2")

        self.login(client, self.user)
        self.assertEqual(len(gen_wiki_category_choices()), 2)

        self.login(client, self.user2)
        self.assertEqual(len(gen_wiki_category_choices()), 2)

    def test_prepare_wiki_nav(self, app, client):
        from app.wiki.helpers import prepare_wiki_nav

        self.login(client, self.admin)
        self.assertEqual(len(prepare_wiki_nav()), 2)

        self.login(client, self.moderator)
        self.assertEqual(len(prepare_wiki_nav()), 3)

        self.login(client, self.user)
        self.assertEqual(len(prepare_wiki_nav()), 2)

        self.login(client, self.user2)
        self.assertEqual(len(prepare_wiki_nav()), 2)

    def test_search_wiki_text(self, app, client):
        from app.wiki.helpers import search_wiki_text

        self.set_up_content()

        self.login(client, self.admin)
        results = search_wiki_text("Keyword1")
        results = [id_ for (id_, x, y) in results]
        self.assertEqual(len(results), 4)
        self.assertTrue(self.wiki_entry1.id in results)
        self.assertTrue(self.wiki_entry2.id in results)
        self.assertTrue(self.wiki_entry3.id in results)
        self.assertTrue(self.wiki_entry5.id in results)

        results = search_wiki_text("Keyword2")
        self.assertEqual(len(results), 2)
        results = [id_ for (id_, x, y) in results]
        self.assertFalse(self.wiki_entry4 in results)

        self.assertEqual(len(search_wiki_text("Keyword3")), 0)
        self.assertEqual(search_wiki_text("keyword1"), search_wiki_text("Keyword1"))

        self.login(client, self.moderator)
        self.assertEqual(len(search_wiki_text("Keyword1")), 4)
        self.assertEqual(len(search_wiki_text("Keyword2")), 2)

        self.login(client, self.user)
        self.assertEqual(len(search_wiki_text("Keyword1")), 3)
        self.assertEqual(len(search_wiki_text("Keyword2")), 1)

        self.login(client, self.user2)
        self.assertEqual(len(search_wiki_text("Keyword1")), 3)
        self.assertEqual(len(search_wiki_text("Keyword2")), 1)

    def test_get_search_context(self, app, client):
        from app.wiki.helpers import get_search_context

        self.set_up_content()

        self.assertEqual(get_search_context("Keyword1", self.wiki_entry1.content),
                         "Keyword1 is at the beginning of t")
        self.assertEqual(get_search_context("Keyword1", self.wiki_entry2.content),
                         "This text contains Keyword1 and Keyword2 in the midd")
        self.assertEqual(get_search_context("Keyword1", self.wiki_entry3.content),
                         "This text contains Keyword1 and ends with Keyword2.")
        self.assertEqual(get_search_context("Keyword1", self.wiki_entry4.content),
                         " starts this text, while Keyword1 is in the middle.")
        self.assertEqual(get_search_context("Keyword1", self.wiki_entry5.content),
                         "t just ends in lowercase keyword1.")

        self.assertEqual(get_search_context("Keyword2", self.wiki_entry2.content),
                         "xt contains Keyword1 and Keyword2 in the middle.")
        self.assertEqual(get_search_context("Keyword2", self.wiki_entry3.content),
                         "s Keyword1 and ends with Keyword2.")
        self.assertEqual(get_search_context("Keyword2", self.wiki_entry4.content),
                         "Keyword2 starts this text, while ")

    def test_prepare_search_result(self, app, client):
        """
        This function basically just calls get_search_context for every text search result
        """
        from app.wiki.helpers import prepare_search_result, search_wiki_text

        self.set_up_content()

        self.login(client, self.admin)
        results = search_wiki_text("Keyword1")
        self.assertEqual(len(prepare_search_result("Keyword1", results)), len(results))

        results = search_wiki_text("Keyword2")
        self.assertEqual(len(prepare_search_result("Keyword2", results)), len(results))

    def test_search_wiki_tag(self, app, client):
        from app.wiki.helpers import search_wiki_tag

        self.set_up_tags()

        self.login(client, self.admin)
        results = search_wiki_tag("tag1")
        self.assertEqual(len(results), 4)
        results = dict(results)
        self.assertTrue(self.wiki_entry1.id in results)
        self.assertTrue(self.wiki_entry2.id in results)
        self.assertTrue(self.wiki_entry3.id in results)
        self.assertTrue(self.wiki_entry5.id in results)

        results = search_wiki_tag("tag2")
        self.assertEqual(len(results), 2)
        results = dict(results)
        self.assertFalse(self.wiki_entry4 in results)

        self.assertEqual(len(search_wiki_tag("tag3")), 0)
        self.assertEqual(search_wiki_tag("Tag1"), search_wiki_tag("tag1"))

        self.login(client, self.moderator)
        self.assertEqual(len(search_wiki_tag("tag1")), 4)
        self.assertEqual(len(search_wiki_tag("tag2")), 2)

        self.login(client, self.user)
        self.assertEqual(len(search_wiki_tag("tag1")), 3)
        self.assertEqual(len(search_wiki_tag("tag2")), 1)

        self.login(client, self.user2)
        self.assertEqual(len(search_wiki_tag("tag1")), 3)
        self.assertEqual(len(search_wiki_tag("tag2")), 1)

    def test_get_recently_created(self, app, client):
        from app.wiki.helpers import get_recently_created

        self.login(client, self.admin)
        recent = get_recently_created()
        self.assertEqual(len(recent), 4)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry5.id)
        self.assertEqual(recent[1], self.wiki_entry3.id)
        self.assertEqual(recent[2], self.wiki_entry2.id)
        self.assertEqual(recent[3], self.wiki_entry1.id)

        self.login(client, self.moderator)
        recent = get_recently_created()
        self.assertEqual(len(recent), 4)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry5.id)
        self.assertEqual(recent[1], self.wiki_entry4.id)
        self.assertEqual(recent[2], self.wiki_entry3.id)
        self.assertEqual(recent[3], self.wiki_entry1.id)

        self.login(client, self.user)
        recent = get_recently_created()
        self.assertEqual(len(recent), 4)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry6.id)
        self.assertEqual(recent[1], self.wiki_entry5.id)
        self.assertEqual(recent[2], self.wiki_entry3.id)
        self.assertEqual(recent[3], self.wiki_entry1.id)

        self.login(client, self.user2)
        recent = get_recently_created()
        self.assertEqual(len(recent), 3)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry5.id)
        self.assertEqual(recent[1], self.wiki_entry3.id)
        self.assertEqual(recent[2], self.wiki_entry1.id)

        # test that its capped at 5
        self.wiki_entry2.is_visible = True
        self.wiki_entry4.is_visible = True
        self.wiki_entry6.is_visible = True
        self.commit()

        self.assertEqual(len(get_recently_created()), 5)

        # check that it works without any entries
        self.rem_all([self.wiki_entry1, self.wiki_entry2, self.wiki_entry3, self.wiki_entry4,
                      self.wiki_entry5, self.wiki_entry6])
        self.commit()
        self.assertEqual(len(get_recently_created()), 0)

    def test_get_recently_edited(self, app, client):
        from app.wiki.helpers import get_recently_edited

        # check that it works without any edited articles
        self.login(client, self.admin)
        self.assertEqual(len(get_recently_edited()), 0)

        self.set_up_dates(client)

        self.login(client, self.admin)
        recent = get_recently_edited()
        self.assertEqual(len(recent), 4)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry1.id)
        self.assertEqual(recent[1], self.wiki_entry2.id)
        self.assertEqual(recent[2], self.wiki_entry3.id)
        self.assertEqual(recent[3], self.wiki_entry5.id)

        self.login(client, self.moderator)
        recent = get_recently_edited()
        self.assertEqual(len(recent), 4)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry1.id)
        self.assertEqual(recent[1], self.wiki_entry3.id)
        self.assertEqual(recent[2], self.wiki_entry4.id)
        self.assertEqual(recent[3], self.wiki_entry5.id)

        self.login(client, self.user)
        recent = get_recently_edited()
        self.assertEqual(len(recent), 4)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry1.id)
        self.assertEqual(recent[1], self.wiki_entry3.id)
        self.assertEqual(recent[2], self.wiki_entry5.id)
        self.assertEqual(recent[3], self.wiki_entry6.id)

        self.login(client, self.user2)
        recent = get_recently_edited()
        self.assertEqual(len(recent), 3)
        recent = [id_ for (id_, _, _, _) in recent]
        self.assertEqual(recent[0], self.wiki_entry1.id)
        self.assertEqual(recent[1], self.wiki_entry3.id)
        self.assertEqual(recent[2], self.wiki_entry5.id)

        # test that its capped at 5
        self.wiki_entry2.is_visible = True
        self.wiki_entry4.is_visible = True
        self.wiki_entry6.is_visible = True
        self.commit()

        self.assertEqual(len(get_recently_edited()), 5)

    def test_gen_category_strings(self, app, client):
        from app.wiki.helpers import gen_category_strings

        self.login(client, self.admin)
        categories = gen_category_strings()
        self.assertEqual(len(categories), 1)  # Choose + Cat 1
        self.assertTrue("Cat 1" in categories)

        self.login(client, self.moderator)
        categories = gen_category_strings()
        self.assertEqual(len(categories), 2)
        self.assertTrue("Cat 1" in categories)
        self.assertTrue("Cat 2" in categories)

        self.login(client, self.user)
        self.assertEqual(len(gen_category_strings()), 1)

        self.login(client, self.user2)
        self.assertEqual(len(gen_category_strings()), 1)

    def set_up_content(self):
        self.wiki_entry1.content = "Keyword1 is at the beginning of this text"
        self.wiki_entry2.content = "This text contains Keyword1 and Keyword2 in the middle."
        self.wiki_entry3.content = "This text contains Keyword1 and ends with Keyword2."
        self.wiki_entry4.content = "Keyword2 starts this text, while Keyword1 is in the middle."
        self.wiki_entry5.content = "This text just ends in lowercase keyword1."
        self.wiki_entry6.content = "This text has the word Keyword in it, but without the numbers."
        self.commit()

    def set_up_tags(self):
        self.wiki_entry1.tags = "tag1"
        self.wiki_entry2.tags = "tag1 tag2"
        self.wiki_entry3.tags = "tag1 tag2"
        self.wiki_entry4.tags = "tag1 tag2"
        self.wiki_entry5.tags = "tag1"
        self.wiki_entry6.tags = ""
        self.commit()

    def set_up_dates(self, client):
        """
        'edit' all wiki articles so that edited_by and edited are set
        Reverse order from the created-date is deliberate.
        Need a commit() after each so that sqlalchemy does no reordering (or something)
        """
        self.login(client, self.admin)
        self.wiki_entry6.content = "edit"
        self.commit()
        self.wiki_entry5.content = "edit"
        self.commit()
        self.wiki_entry4.content = "edit"
        self.commit()
        self.wiki_entry3.content = "edit"
        self.commit()
        self.wiki_entry2.content = "edit"
        self.commit()
        self.wiki_entry1.content = "edit"
        self.commit()
