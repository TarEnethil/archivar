import tempfile
from tests import BaseTestCase, FakeFile
from flask import get_flashed_messages


class MediaHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_media()

    def test_gen_media_category_choices(self, app, client):
        from app.media.helpers import gen_media_category_choices

        self.assertEqual(len(gen_media_category_choices()), 3)

    def test_upload_media_file(self, app, client):
        import os
        from app.media.helpers import upload_media_file

        img = FakeFile(filename="test.jpg")
        img_fail = FakeFile(filename="test.jpg", upload_should_fail=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["MEDIA_DIR"] = tmpdir

            success, filename, size = upload_media_file(img)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))
            self.assertTrue(success)
            self.assertEqual(size, 31193)

            success, filename, size = upload_media_file(img, filename="fixname.jpg")
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))
            self.assertTrue(success)
            self.assertEqual(filename, "fixname.jpg")
            self.assertEqual(size, 31193)

            client.get("/")
            # flash() (used in case of failure) needs a http context
            with client.session_transaction():
                success, filename, size = upload_media_file(img_fail)
                self.assertFalse(os.path.exists(os.path.join(tmpdir, filename)))
                self.assertFalse(success)
                flashes = get_flashed_messages()
                self.assertEqual(len(flashes), 1)
                self.assertTrue("intentionally" in flashes[0])

    def test_generate_media_thumbnail(self, app, client):
        import os
        from app.media.helpers import generate_media_thumbnail

        img = FakeFile(filename="test.jpg")

        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["MEDIA_DIR"] = tmpdir
            os.mkdir(os.path.join(tmpdir, "thumbnails"))

            # copy image to fake upload folder
            img.save(os.path.join(tmpdir, img.filename))
            self.assertTrue(generate_media_thumbnail(img.filename))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "thumbnails", img.filename)))

            # flash() needs context
            client.get("/")
            # try to generate thumbnail of non existing image (test fail path)
            with client.session_transaction():
                self.assertFalse(generate_media_thumbnail("will_fail.png"))
                flashes = get_flashed_messages()
                self.assertEqual(len(flashes), 1)
                self.assertTrue("No such file" in flashes[0])

    def test_get_media(self, app, client):
        from app.media.helpers import get_media

        self.login(client, self.admin)
        self.assertEqual(len(get_media()), 4)
        self.assertEqual(len(get_media(self.media_cat1.id)), 3)
        self.assertEqual(len(get_media(self.media_cat2.id)), 1)
        self.assertEqual(len(get_media(self.media_cat3.id)), 0)

        self.login(client, self.moderator)
        self.assertEqual(len(get_media()), 4)
        self.assertEqual(len(get_media(self.media_cat1.id)), 2)
        self.assertEqual(len(get_media(self.media_cat2.id)), 2)
        self.assertEqual(len(get_media(self.media_cat3.id)), 0)

        self.login(client, self.user)
        self.assertEqual(len(get_media()), 4)
        self.assertEqual(len(get_media(self.media_cat1.id)), 2)
        self.assertEqual(len(get_media(self.media_cat2.id)), 1)
        self.assertEqual(len(get_media(self.media_cat3.id)), 1)

        self.login(client, self.user2)
        self.assertEqual(len(get_media()), 3)
        self.assertEqual(len(get_media(self.media_cat1.id)), 2)
        self.assertEqual(len(get_media(self.media_cat2.id)), 1)
        self.assertEqual(len(get_media(self.media_cat3.id)), 0)
