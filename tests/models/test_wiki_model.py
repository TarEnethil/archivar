from tests import BaseTestCase


class WikiModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_wiki()

    def test_split_tags(self, app, client):
        self.wiki_entry1.tags = "tag1 tag2 tag3"
        tags = self.wiki_entry1.split_tags()
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0], "tag1")
        self.assertEqual(tags[1], "tag2")
        self.assertEqual(tags[2], "tag3")

    def test_permissions(self, app, client):
        ########
        # Admin
        ########
        # Owns Entry 1 and 2
        self.login(client, self.admin)
        self.assertTrue(self.wiki_entry1.is_viewable_by_user())
        self.assertTrue(self.wiki_entry1.is_editable_by_user())
        self.assertTrue(self.wiki_entry1.is_hideable_by_user())
        self.assertTrue(self.wiki_entry1.is_deletable_by_user())

        self.assertTrue(self.wiki_entry2.is_viewable_by_user())
        self.assertTrue(self.wiki_entry2.is_editable_by_user())
        self.assertTrue(self.wiki_entry2.is_hideable_by_user())
        self.assertTrue(self.wiki_entry2.is_deletable_by_user())

        self.assertTrue(self.wiki_entry3.is_viewable_by_user())
        self.assertTrue(self.wiki_entry3.is_editable_by_user())
        self.assertFalse(self.wiki_entry3.is_hideable_by_user())
        self.assertTrue(self.wiki_entry3.is_deletable_by_user())

        self.assertFalse(self.wiki_entry4.is_viewable_by_user())
        self.assertFalse(self.wiki_entry4.is_editable_by_user())
        self.assertFalse(self.wiki_entry4.is_hideable_by_user())
        self.assertFalse(self.wiki_entry4.is_deletable_by_user())

        self.assertTrue(self.wiki_entry5.is_viewable_by_user())
        self.assertTrue(self.wiki_entry5.is_editable_by_user())
        self.assertFalse(self.wiki_entry5.is_hideable_by_user())
        self.assertTrue(self.wiki_entry5.is_deletable_by_user())

        self.assertFalse(self.wiki_entry6.is_viewable_by_user())
        self.assertFalse(self.wiki_entry6.is_editable_by_user())
        self.assertFalse(self.wiki_entry6.is_hideable_by_user())
        self.assertFalse(self.wiki_entry6.is_deletable_by_user())

        ########
        # Moderator
        ########
        # Owns Entry 3 and 4
        self.login(client, self.moderator)
        self.assertTrue(self.wiki_entry1.is_viewable_by_user())
        self.assertTrue(self.wiki_entry1.is_editable_by_user())
        self.assertFalse(self.wiki_entry1.is_hideable_by_user())
        self.assertTrue(self.wiki_entry1.is_deletable_by_user())

        self.assertFalse(self.wiki_entry2.is_viewable_by_user())
        self.assertFalse(self.wiki_entry2.is_editable_by_user())
        self.assertFalse(self.wiki_entry2.is_hideable_by_user())
        self.assertFalse(self.wiki_entry2.is_deletable_by_user())

        self.assertTrue(self.wiki_entry3.is_viewable_by_user())
        self.assertTrue(self.wiki_entry3.is_editable_by_user())
        self.assertTrue(self.wiki_entry3.is_hideable_by_user())
        self.assertTrue(self.wiki_entry3.is_deletable_by_user())

        self.assertTrue(self.wiki_entry4.is_viewable_by_user())
        self.assertTrue(self.wiki_entry4.is_editable_by_user())
        self.assertTrue(self.wiki_entry4.is_hideable_by_user())
        self.assertTrue(self.wiki_entry4.is_deletable_by_user())

        self.assertTrue(self.wiki_entry5.is_viewable_by_user())
        self.assertTrue(self.wiki_entry5.is_editable_by_user())
        self.assertFalse(self.wiki_entry5.is_hideable_by_user())
        self.assertTrue(self.wiki_entry5.is_deletable_by_user())

        self.assertFalse(self.wiki_entry6.is_viewable_by_user())
        self.assertFalse(self.wiki_entry6.is_editable_by_user())
        self.assertFalse(self.wiki_entry6.is_hideable_by_user())
        self.assertFalse(self.wiki_entry6.is_deletable_by_user())

        ########
        # User
        ########
        # Owns Entry 5 and 6
        self.login(client, self.user)
        self.assertTrue(self.wiki_entry1.is_viewable_by_user())
        self.assertTrue(self.wiki_entry1.is_editable_by_user())
        self.assertFalse(self.wiki_entry1.is_hideable_by_user())
        self.assertFalse(self.wiki_entry1.is_deletable_by_user())

        self.assertFalse(self.wiki_entry2.is_viewable_by_user())
        self.assertFalse(self.wiki_entry2.is_editable_by_user())
        self.assertFalse(self.wiki_entry2.is_hideable_by_user())
        self.assertFalse(self.wiki_entry2.is_deletable_by_user())

        self.assertTrue(self.wiki_entry3.is_viewable_by_user())
        self.assertTrue(self.wiki_entry3.is_editable_by_user())
        self.assertFalse(self.wiki_entry3.is_hideable_by_user())
        self.assertFalse(self.wiki_entry3.is_deletable_by_user())

        self.assertFalse(self.wiki_entry4.is_viewable_by_user())
        self.assertFalse(self.wiki_entry4.is_editable_by_user())
        self.assertFalse(self.wiki_entry4.is_hideable_by_user())
        self.assertFalse(self.wiki_entry4.is_deletable_by_user())

        self.assertTrue(self.wiki_entry5.is_viewable_by_user())
        self.assertTrue(self.wiki_entry5.is_editable_by_user())
        self.assertTrue(self.wiki_entry5.is_hideable_by_user())
        self.assertTrue(self.wiki_entry5.is_deletable_by_user())

        self.assertTrue(self.wiki_entry6.is_viewable_by_user())
        self.assertTrue(self.wiki_entry6.is_editable_by_user())
        self.assertTrue(self.wiki_entry6.is_hideable_by_user())
        self.assertTrue(self.wiki_entry6.is_deletable_by_user())

        ########
        # User2
        ########
        # Does not own any wiki_entry
        self.login(client, self.user2)
        self.assertTrue(self.wiki_entry1.is_viewable_by_user())
        self.assertTrue(self.wiki_entry1.is_editable_by_user())
        self.assertFalse(self.wiki_entry1.is_hideable_by_user())
        self.assertFalse(self.wiki_entry1.is_deletable_by_user())

        self.assertFalse(self.wiki_entry2.is_viewable_by_user())
        self.assertFalse(self.wiki_entry2.is_editable_by_user())
        self.assertFalse(self.wiki_entry2.is_hideable_by_user())
        self.assertFalse(self.wiki_entry2.is_deletable_by_user())

        self.assertTrue(self.wiki_entry3.is_viewable_by_user())
        self.assertTrue(self.wiki_entry3.is_editable_by_user())
        self.assertFalse(self.wiki_entry3.is_hideable_by_user())
        self.assertFalse(self.wiki_entry3.is_deletable_by_user())

        self.assertFalse(self.wiki_entry4.is_viewable_by_user())
        self.assertFalse(self.wiki_entry4.is_editable_by_user())
        self.assertFalse(self.wiki_entry4.is_hideable_by_user())
        self.assertFalse(self.wiki_entry4.is_deletable_by_user())

        self.assertTrue(self.wiki_entry5.is_viewable_by_user())
        self.assertTrue(self.wiki_entry5.is_editable_by_user())
        self.assertFalse(self.wiki_entry5.is_hideable_by_user())
        self.assertFalse(self.wiki_entry5.is_deletable_by_user())

        self.assertFalse(self.wiki_entry6.is_viewable_by_user())
        self.assertFalse(self.wiki_entry6.is_editable_by_user())
        self.assertFalse(self.wiki_entry6.is_hideable_by_user())
        self.assertFalse(self.wiki_entry6.is_deletable_by_user())
