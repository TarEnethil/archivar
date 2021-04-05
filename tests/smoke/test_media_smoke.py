import tempfile
import os
from app.media.models import MediaSetting
from flask import url_for
from tests import SmokeWrapper, FakeFile


class MediaSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_media()

        self.add(MediaSetting())
        self.media1.filesize = 100
        self.media2.filesize = 100
        self.media3.filesize = 100
        self.media4.filesize = 100
        self.media5.filesize = 100
        self.media6.filesize = 100
        self.commit()

    def set_up_common_urls(self):
        self.common_urls = [url_for("media.list_by_cat", c_id=self.media_cat1.id, c_name=self.media_cat1.name),
                            url_for("media.list_by_cat", c_id=self.media_cat2.id, c_name=self.media_cat2.name),
                            url_for("media.list_by_cat", c_id=self.media_cat3.id, c_name=self.media_cat3.name),
                            self.media1.view_url(), self.media3.view_url(), self.media5.view_url()]
        self.common_endpoints = ["media.index", "media.upload"]

    def serve_test(self, app, client):
        """
        test direct serving of files + thumbnails
        """
        img = FakeFile(filename="test.jpg")

        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["MEDIA_DIR"] = tmpdir
            os.mkdir(os.path.join(tmpdir, "thumbnails"))

            # copy image to fake upload folder + thumbnail
            img.save(os.path.join(tmpdir, img.filename))
            img.save(os.path.join(tmpdir, "thumbnails", img.filename))

            # media3 is test.jpg
            self.assertHTTPOK(client, self.media3.serve_url(), url=True)
            self.assertHTTPOK(client, self.media3.thumbnail_url(), url=True)

    def profile_picture_test(self, app, client):
        """
        test direct serving of profile pictures + thumbnails
        """
        self.set_up_characters()  # so that we have something to test (default) profile picture

        img = FakeFile(filename="test.jpg")
        self.char_admin.profile_picture = img.filename

        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["PROFILE_PICTURE_DIR"] = tmpdir
            os.mkdir(os.path.join(tmpdir, "thumbnails"))

            # copy image to fake upload folder + thumbnail
            img.save(os.path.join(tmpdir, img.filename))
            img.save(os.path.join(tmpdir, "thumbnails", img.filename))

            # media3 is test.jpg
            self.assertHTTPOK(client, self.char_admin.profile_picture_url(), url=True)
            self.assertHTTPOK(client, self.char_admin.profile_thumbnail_url(), url=True)

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, self.media1.edit_url(), url=True)
        self.assertHTTPOK(client, self.media1.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.media2.view_url(), url=True)
        self.assertHTTPOK(client, self.media2.edit_url(), url=True)
        self.assertHTTPOK(client, self.media2.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, "media.settings")
        self.assertHTTPOK(client, "media.category_create")
        self.assertHTTPOK(client, self.media_cat1.edit_url(), url=True)

        self.serve_test(app, client)
        self.profile_picture_test(app, client)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, self.media3.edit_url(), url=True)
        self.assertHTTPOK(client, self.media3.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.media4.view_url(), url=True)
        self.assertHTTPOK(client, self.media4.edit_url(), url=True)
        self.assertHTTPOK(client, self.media4.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, "media.settings")
        self.assertHTTPOK(client, "media.category_create")
        self.assertHTTPOK(client, self.media_cat1.edit_url(), url=True)

        self.serve_test(app, client)
        self.profile_picture_test(app, client)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, self.media5.edit_url(), url=True)
        self.assertHTTPOK(client, self.media5.delete_url(), url=True, follow=True)

        self.assertHTTPOK(client, self.media6.view_url(), url=True)
        self.assertHTTPOK(client, self.media6.edit_url(), url=True)
        self.assertHTTPOK(client, self.media6.delete_url(), url=True, follow=True)

        self.serve_test(app, client)
        self.profile_picture_test(app, client)
