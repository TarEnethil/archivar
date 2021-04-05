from app.media.models import MediaItem
from tests import BaseTestCase


class MediaModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_media()

    def test_get_file_ext(self, app, client):
        self.assertEqual(self.media1.get_file_ext(), "pdf")
        self.assertEqual(self.media2.get_file_ext(), "png")
        self.assertEqual(self.media3.get_file_ext(), "jpg")
        self.assertEqual(self.media4.get_file_ext(), "tar")
        self.assertEqual(self.media5.get_file_ext(), "bz2")
        self.assertEqual(self.media6.get_file_ext(), "zip")

        self.assertEqual(MediaItem(filename="test.PNG").get_file_ext(), "png")
        self.assertEqual(MediaItem(filename="test.pnG").get_file_ext(), "png")

    def test_is_image(self, app, client):
        self.assertFalse(self.media1.is_image())
        self.assertTrue(self.media2.is_image())
        self.assertTrue(self.media3.is_image())
        self.assertFalse(self.media4.is_image())
        self.assertFalse(self.media5.is_image())
        self.assertFalse(self.media6.is_image())

        self.assertTrue(MediaItem(filename="test.GIF").is_image())
        self.assertTrue(MediaItem(filename="test.JpEg").is_image())
        self.assertTrue(MediaItem(filename="test.Png").is_image())

        self.assertFalse(MediaItem(filename="test.jjpg").is_image())
        self.assertFalse(MediaItem(filename="test.pngg").is_image())

    def test_get_icon_str(self, app, client):
        self.assertEqual(self.media1.get_icon_str(), "file-pdf")
        self.assertEqual(self.media2.get_icon_str(), "file-alt")
        self.assertEqual(self.media3.get_icon_str(), "file-alt")
        self.assertEqual(self.media4.get_icon_str(), "file-archive")
        self.assertEqual(self.media5.get_icon_str(), "file-archive")
        self.assertEqual(self.media6.get_icon_str(), "file-archive")

    def test_permissions(self, app, client):
        ########
        # Admin
        ########
        # Owns Media 1 and 2
        self.login(client, self.admin)
        self.assertTrue(self.media1.is_viewable_by_user())
        self.assertTrue(self.media1.is_editable_by_user())
        self.assertTrue(self.media1.is_hideable_by_user())
        self.assertTrue(self.media1.is_deletable_by_user())

        self.assertTrue(self.media2.is_viewable_by_user())
        self.assertTrue(self.media2.is_editable_by_user())
        self.assertTrue(self.media2.is_hideable_by_user())
        self.assertTrue(self.media2.is_deletable_by_user())

        self.assertTrue(self.media3.is_viewable_by_user())
        self.assertTrue(self.media3.is_editable_by_user())
        self.assertFalse(self.media3.is_hideable_by_user())
        self.assertTrue(self.media3.is_deletable_by_user())

        self.assertFalse(self.media4.is_viewable_by_user())
        self.assertFalse(self.media4.is_editable_by_user())
        self.assertFalse(self.media4.is_hideable_by_user())
        self.assertFalse(self.media4.is_deletable_by_user())

        self.assertTrue(self.media5.is_viewable_by_user())
        self.assertTrue(self.media5.is_editable_by_user())
        self.assertFalse(self.media5.is_hideable_by_user())
        self.assertTrue(self.media5.is_deletable_by_user())

        self.assertFalse(self.media6.is_viewable_by_user())
        self.assertFalse(self.media6.is_editable_by_user())
        self.assertFalse(self.media6.is_hideable_by_user())
        self.assertFalse(self.media6.is_deletable_by_user())

        ########
        # Moderator
        ########
        # Owns Media 3 and 4
        self.login(client, self.moderator)
        self.assertTrue(self.media1.is_viewable_by_user())
        self.assertTrue(self.media1.is_editable_by_user())
        self.assertFalse(self.media1.is_hideable_by_user())
        self.assertTrue(self.media1.is_deletable_by_user())

        self.assertFalse(self.media2.is_viewable_by_user())
        self.assertFalse(self.media2.is_editable_by_user())
        self.assertFalse(self.media2.is_hideable_by_user())
        self.assertFalse(self.media2.is_deletable_by_user())

        self.assertTrue(self.media3.is_viewable_by_user())
        self.assertTrue(self.media3.is_editable_by_user())
        self.assertTrue(self.media3.is_hideable_by_user())
        self.assertTrue(self.media3.is_deletable_by_user())

        self.assertTrue(self.media4.is_viewable_by_user())
        self.assertTrue(self.media4.is_editable_by_user())
        self.assertTrue(self.media4.is_hideable_by_user())
        self.assertTrue(self.media4.is_deletable_by_user())

        self.assertTrue(self.media5.is_viewable_by_user())
        self.assertTrue(self.media5.is_editable_by_user())
        self.assertFalse(self.media5.is_hideable_by_user())
        self.assertTrue(self.media5.is_deletable_by_user())

        self.assertFalse(self.media6.is_viewable_by_user())
        self.assertFalse(self.media6.is_editable_by_user())
        self.assertFalse(self.media6.is_hideable_by_user())
        self.assertFalse(self.media6.is_deletable_by_user())

        ########
        # User
        ########
        # Owns Media 5 and 6
        self.login(client, self.user)
        self.assertTrue(self.media1.is_viewable_by_user())
        self.assertFalse(self.media1.is_editable_by_user())
        self.assertFalse(self.media1.is_hideable_by_user())
        self.assertFalse(self.media1.is_deletable_by_user())

        self.assertFalse(self.media2.is_viewable_by_user())
        self.assertFalse(self.media2.is_editable_by_user())
        self.assertFalse(self.media2.is_hideable_by_user())
        self.assertFalse(self.media2.is_deletable_by_user())

        self.assertTrue(self.media3.is_viewable_by_user())
        self.assertFalse(self.media3.is_editable_by_user())
        self.assertFalse(self.media3.is_hideable_by_user())
        self.assertFalse(self.media3.is_deletable_by_user())

        self.assertFalse(self.media4.is_viewable_by_user())
        self.assertFalse(self.media4.is_editable_by_user())
        self.assertFalse(self.media4.is_hideable_by_user())
        self.assertFalse(self.media4.is_deletable_by_user())

        self.assertTrue(self.media5.is_viewable_by_user())
        self.assertTrue(self.media5.is_editable_by_user())
        self.assertTrue(self.media5.is_hideable_by_user())
        self.assertTrue(self.media5.is_deletable_by_user())

        self.assertTrue(self.media6.is_viewable_by_user())
        self.assertTrue(self.media6.is_editable_by_user())
        self.assertTrue(self.media6.is_hideable_by_user())
        self.assertTrue(self.media6.is_deletable_by_user())

        ########
        # User2
        ########
        # Does not own any media
        self.login(client, self.user2)
        self.assertTrue(self.media1.is_viewable_by_user())
        self.assertFalse(self.media1.is_editable_by_user())
        self.assertFalse(self.media1.is_hideable_by_user())
        self.assertFalse(self.media1.is_deletable_by_user())

        self.assertFalse(self.media2.is_viewable_by_user())
        self.assertFalse(self.media2.is_editable_by_user())
        self.assertFalse(self.media2.is_hideable_by_user())
        self.assertFalse(self.media2.is_deletable_by_user())

        self.assertTrue(self.media3.is_viewable_by_user())
        self.assertFalse(self.media3.is_editable_by_user())
        self.assertFalse(self.media3.is_hideable_by_user())
        self.assertFalse(self.media3.is_deletable_by_user())

        self.assertFalse(self.media4.is_viewable_by_user())
        self.assertFalse(self.media4.is_editable_by_user())
        self.assertFalse(self.media4.is_hideable_by_user())
        self.assertFalse(self.media4.is_deletable_by_user())

        self.assertTrue(self.media5.is_viewable_by_user())
        self.assertFalse(self.media5.is_editable_by_user())
        self.assertFalse(self.media5.is_hideable_by_user())
        self.assertFalse(self.media5.is_deletable_by_user())

        self.assertFalse(self.media6.is_viewable_by_user())
        self.assertFalse(self.media6.is_editable_by_user())
        self.assertFalse(self.media6.is_hideable_by_user())
        self.assertFalse(self.media6.is_deletable_by_user())
