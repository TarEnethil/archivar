import tempfile
import os
from flask import get_flashed_messages
from tests import BaseTestCase, FakeFile, FakeField, FakeForm
from wtforms.validators import ValidationError


class AppHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def test_flash_no_permission(self, app, client):
        from app.helpers import flash_no_permission

        client.get("/")
        with client.session_transaction():
            flash_no_permission()
            flashes = get_flashed_messages()
            self.assertEqual(len(flashes), 1)
            self.assertTrue("No permission" in flashes[0])

        client.get("/")
        with client.session_transaction():
            flash_no_permission(msg="Custom Message")
            flashes = get_flashed_messages()
            self.assertEqual(len(flashes), 1)
            self.assertTrue("Custom Message" in flashes[0])

    def test_deny_access(self, app, client):
        from app.helpers import deny_access

        client.get("/")
        with client.session_transaction():
            resp = deny_access("main.index")
            self.assertEqual(resp.status_code, 302)
            flashes = get_flashed_messages()
            self.assertEqual(len(flashes), 1)
            self.assertTrue("No permission" in flashes[0])

        client.get("/")
        # flash() (used in case of failure) needs a http context
        with client.session_transaction():
            resp = deny_access("main.index", msg="Custom Message")
            self.assertEqual(resp.status_code, 302)
            flashes = get_flashed_messages()
            self.assertEqual(len(flashes), 1)
            self.assertTrue("Custom Message" in flashes[0])

    def test_page_title(self, app, client):
        from app.helpers import page_title
        from flask import current_app

        self.assertEqual(page_title("Test"), "Test :: Archivar")

        current_app.config["PAGE_TITLE_SUFFIX"] = "-- Suffix"
        self.assertEqual(page_title("Test"), "Test -- Suffix")

        with self.assertRaises(UserWarning):
            page_title("")

        with self.assertRaises(UserWarning):
            page_title(None)

    def test_stretch_color(self, app, client):
        from app.helpers import stretch_color

        self.assertEqual(stretch_color("#fff"), "#ffffff")
        self.assertEqual(stretch_color("#abc"), "#aabbcc")
        self.assertEqual(stretch_color("abc"), "abc")

    def test_count_rows(self, app, client):
        from app.helpers import count_rows
        from app.user.models import User

        self.assertEqual(count_rows(User), 0)

        self.set_up_users()
        self.assertEqual(count_rows(User), 4)

    def test_unique_filename(self, app, client):
        from app.helpers import unique_filename
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            uniq = unique_filename(tmpdir, "my -filename")

            self.assertTrue(" " not in uniq)

            Path(os.path.join(tmpdir), uniq).touch()

            uniq2 = unique_filename(tmpdir, "my -filename")

            self.assertNotEqual(uniq, uniq2)

    def test_generate_thumbnail(self, app, client):
        from app.helpers import generate_thumbnail
        from PIL import Image

        img = FakeFile(filename="test.jpg")

        with tempfile.TemporaryDirectory() as tmpdir:
            os.mkdir(os.path.join(tmpdir, "thumbnails"))

            # copy image to fake upload folder
            img.save(os.path.join(tmpdir, img.filename))
            self.assertTrue(generate_thumbnail(tmpdir, img.filename, 150, 150))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "thumbnails", img.filename)))

            with Image.open(os.path.join(tmpdir, "thumbnails", img.filename)) as img:
                width, height = img.size
                self.assertEqual(height, 150)
                self.assertEqual(width, 150)

    def test_upload_file(self, app, client):
        from app.helpers import upload_file

        img = FakeFile(filename="test.jpg")
        img_fail = FakeFile(filename="test.jpg", upload_should_fail=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            success, filename = upload_file(img, tmpdir)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))

            success, filename = upload_file(img, tmpdir, filename="fixname.jpg")
            self.assertTrue(success)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))
            self.assertEqual(filename, "fixname.jpg")

            client.get("/")
            # flash() (used in case of failure) needs a http context
            with client.session_transaction():
                success, filename = upload_file(img_fail, tmpdir)
                self.assertFalse(success)
                self.assertFalse(os.path.exists(os.path.join(tmpdir, filename)))
                flashes = get_flashed_messages()
                self.assertEqual(len(flashes), 1)
                self.assertTrue("intentionally" in flashes[0])

    def test_delete_profile_picture(self, app, client):
        from app.helpers import delete_profile_picture
        from flask import current_app

        img = FakeFile(filename="test.jpg")

        with tempfile.TemporaryDirectory() as tmpdir:
            current_app.config["PROFILE_PICTURE_DIR"] = tmpdir
            os.mkdir(os.path.join(tmpdir, "thumbnails"))

            img.save(os.path.join(tmpdir, img.filename))
            img.save(os.path.join(tmpdir, "thumbnails", img.filename))

            delete_profile_picture(img.filename)
            self.assertFalse(os.path.exists(os.path.join(tmpdir, img.filename)))
            self.assertFalse(os.path.exists(os.path.join(tmpdir, "thumbnails", img.filename)))

            # check that function does not throw on missing image
            # error path uses flash() -> need session
            client.get("/")
            with client.session_transaction():
                delete_profile_picture("does_not_exist.jpg")

    def test_upload_profile_picture(self, app, client):
        from app.helpers import upload_profile_picture
        from flask import current_app

        img = FakeFile(filename="test.jpg")

        with tempfile.TemporaryDirectory() as tmpdir:
            current_app.config["PROFILE_PICTURE_DIR"] = tmpdir
            os.mkdir(os.path.join(tmpdir, "thumbnails"))

            success, filename = upload_profile_picture(img)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "thumbnails", filename)))

            success, filename = upload_profile_picture(img, filename="fix.jpg")
            self.assertTrue(success)
            self.assertEqual(filename, "fix.jpg")
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "thumbnails", filename)))

    def test_debug_mode(self, app, client):
        from app.helpers import debug_mode
        from flask import current_app

        self.assertFalse(debug_mode())

        current_app.config["DEBUG"] = True
        self.assertTrue(debug_mode())

    def test_urlfriendly(self, app, client):
        from app.helpers import urlfriendly

        friendly = urlfriendly("Ul #öß1!!\"§$%&-<LiNk>")

        self.assertFalse("U" in friendly)
        self.assertFalse("#" in friendly)
        self.assertFalse(" " in friendly)
        self.assertFalse("ö" in friendly)
        self.assertFalse("ß" in friendly)
        self.assertFalse("!" in friendly)
        self.assertFalse("\"" in friendly)
        self.assertFalse("§" in friendly)
        self.assertFalse("$" in friendly)
        self.assertFalse("%" in friendly)
        self.assertFalse("&" in friendly)
        self.assertFalse("<" in friendly)
        self.assertFalse(">" in friendly)

        self.assertEqual(friendly.lower(), friendly)

        friendly = urlfriendly("thistextistdefinitelylongerthan20characters")
        self.assertEqual(friendly, "thistextistdefinitel")

        friendly = urlfriendly("this-text-is-definitely-longer-than-20-characters")
        self.assertEqual(friendly, "this-text-is-definitely")

    def test_icon_fkt(self, app, client):
        """
        TODO: not the most useful test
        """
        from app.helpers import icon_fkt

        self.assertTrue("fa-my-icon", icon_fkt("my-icon"))
        self.assertTrue("fa-my-icon my-class", icon_fkt("my-icon", text_class="my-class"))

    def test_navbar_start(self, app, client):
        """
        TODO: not the most useful test
        """
        from app.helpers import navbar_start

        self.assertTrue("ul" in navbar_start())
        self.assertFalse("mb" in navbar_start(no_margin=True))

    def test_navbar_end(self, app, client):
        """
        TODO: not the most useful test
        """
        from app.helpers import navbar_end

        self.assertTrue("/ul" in navbar_end())

    def test_link(self, app, client):
        """
        TODO: not the most useful test
        """
        from app.helpers import link

        generated_link = link("my-url", "LINK")
        self.assertTrue('href="my-url"' in generated_link)
        self.assertTrue('>LINK</' in generated_link)

        generated_link = link("my-url", "LINK", classes="my-class")
        self.assertTrue('href="my-url"' in generated_link)
        self.assertTrue('>LINK</' in generated_link)
        self.assertTrue('class="my-class"' in generated_link)

        generated_link = link("my-url", "LINK", ids="my-id")
        self.assertTrue('href="my-url"' in generated_link)
        self.assertTrue('>LINK</' in generated_link)
        self.assertTrue('id="my-id"' in generated_link)

    def test_button_internal(self, app, client):
        """
        TODO: not the most useful test
        """
        from app.helpers import button_internal

        btn = button_internal("my-url", "my-text", icon="my-icon", classes="my-class", ids="my-id",
                              icon_text_class="my-icon-class")
        self.assertTrue('href="my-url"' in btn)
        self.assertTrue('my-text<' in btn)
        self.assertTrue('fa-my-icon my-icon-class' in btn)
        self.assertTrue('class="my-class"' in btn)
        self.assertTrue('id="my-id"' in btn)

        # test with icon swapped behind text
        btn = button_internal("my-url", "my-text", icon="my-icon", swap=True)
        self.assertFalse('my-text<' in btn)
        self.assertTrue('>my-text\n' in btn)

    def test_button(self, app, client):
        """
        TODO: not the most useful test
        """
        from app.helpers import button

        btn = button("my-url", "my-text", icon="my-icon", ids="my-id", icon_text_class="my-icon-class")
        self.assertTrue('href="my-url"' in btn)
        self.assertTrue('my-text<' in btn)
        self.assertTrue('fa-my-icon my-icon-class' in btn)
        self.assertTrue('class="btn' in btn)
        self.assertTrue('id="my-id"' in btn)

        # test with icon swapped behind text
        btn = button("my-url", "my-text", icon="my-icon", swap=True)
        self.assertFalse('my-text<' in btn)
        self.assertTrue('>my-text\n' in btn)

    def test_button_nav(self, app, client):
        """
        TODO: not the most useful test
        """
        from app.helpers import button_nav

        btn = button_nav("my-url", "my-text", icon="my-icon", classes="my-class", ids="my-id",
                         icon_text_class="my-icon-class", li_classes="li")
        self.assertTrue('href="my-url"' in btn)
        self.assertTrue('my-text<' in btn)
        self.assertTrue('fa-my-icon my-icon-class' in btn)
        self.assertTrue('class="nav-link my-class"' in btn)
        self.assertTrue('li class="nav-item li"' in btn)
        self.assertTrue('id="my-id"' in btn)

        # test with icon swapped behind text
        btn = button_nav("my-url", "my-text", icon="my-icon", swap=True)
        self.assertFalse('my-text<' in btn)
        self.assertTrue('>my-text\n' in btn)


class AppProcessorsTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def test_load_global_quicklinks(self, app, client):
        from app.processors import load_global_quicklinks
        self.general_setting.quicklinks = 'url1|linktext1\nurl2|linktext2\nurl3\nurl4|linktext4|addendum'

        quicklinks = load_global_quicklinks()
        self.assertEqual(len(quicklinks), 2)
        self.assertEqual("url1", quicklinks[0][0])
        self.assertEqual("linktext1", quicklinks[0][1])
        self.assertEqual("url2", quicklinks[1][0])
        self.assertEqual("linktext2", quicklinks[1][1])

    def test_load_user_quicklinks(self, app, client):
        from app.processors import load_user_quicklinks

        self.set_up_users()
        self.user.quicklinks = 'url1|linktext1\nurl2|linktext2\nurl3\nurl4|linktext4|addendum'
        self.login(client, self.user)

        quicklinks = load_user_quicklinks()
        self.assertEqual(len(quicklinks), 2)
        self.assertEqual("url1", quicklinks[0][0])
        self.assertEqual("linktext1", quicklinks[0][1])
        self.assertEqual("url2", quicklinks[1][0])
        self.assertEqual("linktext2", quicklinks[1][1])

    def test_include_css(self, app, client):
        from app.processors import include_css
        from flask import current_app, get_flashed_messages

        with app.test_request_context("/"):
            # test no throw on empty set
            self.assertEqual("", include_css([]))

            self.assertTrue("bootstrap.min.css" in include_css(["bootstrap"]))

            # test url not external (SERVE_LOCAL=True)
            self.assertFalse("http" in include_css(["bootstrap"]))

            # test multiple-file-include per key
            self.assertTrue("fontawesome.min.css" in include_css(["fontawesome"]))
            self.assertTrue("solid.min.css" in include_css(["fontawesome"]))

            # test includes with multiple keys
            self.assertTrue("bootstrap.min.css" in include_css(["bootstrap", "fontawesome"]))
            self.assertTrue("fontawesome.min.css" in include_css(["bootstrap", "fontawesome"]))

            current_app.config["SERVE_LOCAL"] = False
            self.assertTrue("https" in include_css(["bootstrap"]))

            include_css(["non-existing-package"])
            flashes = get_flashed_messages(category_filter=["warning"])
            self.assertEqual(len(flashes), 1)
            self.assertTrue("non-existing-package" in flashes[0])

    def test_include_js(self, app, client):
        from app.processors import include_js
        from flask import current_app, get_flashed_messages

        with app.test_request_context("/"):
            # test no throw on empty set
            self.assertEqual("", include_js([]))

            # test url not external (SERVE_LOCAL=True)
            self.assertFalse("http" in include_js(["bootstrap"]))

            # test multiple-file-include per key
            self.assertTrue("jquery.min.js" in include_js(["bootstrap"]))
            self.assertTrue("bootstrap.min.js" in include_js(["bootstrap"]))

            # test inclusion of "helper" files
            self.assertTrue("helpers/datatables.js" in include_js(["datatables"]))

            # test includes with multiple keys
            self.assertTrue("leaflet.js" in include_js(["leaflet", "datatables"]))
            self.assertTrue("dataTables.bootstrap.min.js" in include_js(["leaflet", "datatables"]))

            # test small dependency system (markdown-editor needs bootbox)
            self.assertTrue("bootbox" in include_js(["markdown-editor"]))
            self.assertTrue("bootbox" in include_js(["util"]))

            # test "moment.js is included first"
            includes = include_js(["bootstrap-datetimepicker", "moment"])
            idx1 = includes.index("moment")
            idx2 = includes.index("tempusdominus")
            self.assertLess(idx1, idx2)

            current_app.config["SERVE_LOCAL"] = False
            self.assertTrue("https" in include_js(["bootstrap"]))

            include_js(["non-existing-package"])
            flashes = get_flashed_messages(category_filter=["warning"])
            self.assertEqual(len(flashes), 1)
            self.assertTrue("non-existing-package" in flashes[0])

    def test_short_hash(self, app, client):
        from app.processors import short_hash

        self.assertEqual(len(short_hash("my-text")), len("my-text")+4)

    def test_register_processors_and_filters(self, app, client):
        """
        register_processors_and_filters has already happened in test-case-setup.
        check utility processors and template_filters have been registered
        """
        from app.helpers import urlfriendly

        # check that the last installed context_processor returns the expected number of functions
        # TODO: probably not the most useful test
        self.assertEqual(len(app.template_context_processors[None][-1]()), 12)

        self.assertIsNotNone(app.jinja_env.filters["hash"])
        self.assertIsNotNone(app.jinja_env.filters[urlfriendly.__name__])


class AppDecoratorsTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)
        self.set_up_users()

    def okfunc(self):
        return "OK"

    def test_admin_required(self, app, client):
        from app.decorators import admin_required

        self.login(client, self.admin)
        client.get("/")
        resp = admin_required()(self.okfunc)()
        self.assertEqual("OK", resp)

        self.login(client, self.moderator)
        client.get("/")
        resp = admin_required()(self.okfunc)()
        self.assertEqual(302, resp.status_code)

        self.login(client, self.user)
        client.get("/")
        resp = admin_required()(self.okfunc)()
        self.assertEqual(302, resp.status_code)

    def test_moderator_required(self, app, client):
        from app.decorators import moderator_required

        self.login(client, self.admin)
        client.get("/")
        resp = moderator_required()(self.okfunc)()
        self.assertEqual("OK", resp)

        self.login(client, self.moderator)
        client.get("/")
        resp = moderator_required()(self.okfunc)()
        self.assertEqual("OK", resp)

        self.login(client, self.user)
        client.get("/")
        resp = moderator_required()(self.okfunc)()
        self.assertEqual(302, resp.status_code)

    def test_debug_mode_required(self, app, client):
        from app.decorators import debug_mode_required
        from flask import current_app

        self.login(client, self.admin)
        client.get("/")
        resp = debug_mode_required(self.okfunc)()
        self.assertEqual(302, resp.status_code)

        current_app.config["DEBUG"] = True
        self.assertEqual("OK", debug_mode_required(self.okfunc)())


class AppValidatorsTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

    def test_XYZ_Validator(self, app, client):
        from app.validators import XYZ_Validator

        xyz = XYZ_Validator()

        with self.assertRaises(ValidationError):
            xyz(None, FakeField("name", "not-even-one-field"))

        with self.assertRaises(ValidationError):
            xyz(None, FakeField("name", "only-{x}"))

        with self.assertRaises(ValidationError):
            xyz(None, FakeField("name", "{x} and {y}"))

        xyz(None, FakeField("name", "{x} and {y} and {z}"))

    def test_LessThanOrEqual(self, app, client):
        from app.validators import LessThanOrEqual

        lte = LessThanOrEqual("other_field")

        field = FakeField("field", 5)
        other_field = FakeField("other_field", 10)

        # 5 <= 10 is OK (no raise)
        lte(FakeForm([field, other_field]), field)

        other_field.data = 5
        # 5 <= 5 is OK (no raise)
        lte(FakeForm([field, other_field]), field)

        other_field.data = 1

        # 5 <= 1 is not OK -> raise
        with self.assertRaises(ValidationError):
            lte(FakeForm([field, other_field]), field)

    def test_GreaterThanOrEqual(self, app, client):
        from app.validators import GreaterThanOrEqual

        gte = GreaterThanOrEqual("other_field")

        field = FakeField("field", 10)
        other_field = FakeField("other_field", 5)

        # 10 >= 5 is OK (no raise)
        gte(FakeForm([field, other_field]), field)

        other_field.data = 10
        # 10 >= 10 is OK (no raise)
        gte(FakeForm([field, other_field]), field)

        other_field.data = 15

        # 10 >= 15 is not OK -> raise
        with self.assertRaises(ValidationError):
            gte(FakeForm([field, other_field]), field)

    def test_YearPerEpochValidator(self, app, client):
        from app.validators import YearPerEpochValidator

        self.set_up_users()
        self.set_up_epochs()

        ype = YearPerEpochValidator("epoch")

        year = FakeField("year", 1)
        epoch = FakeField("epoch", self.epochs[0].id)

        # year 1 epoch 1 is valid
        ype(FakeForm([year, epoch]), year)

        # negative years are invalid
        year.data = -1
        with self.assertRaises(ValidationError):
            ype(FakeForm([year, epoch]), year)

        year.data = 0
        with self.assertRaises(ValidationError):
            ype(FakeForm([year, epoch]), year)

        # year 101 is invalid for epoch 1
        year.data = 101
        with self.assertRaises(ValidationError):
            ype(FakeForm([year, epoch]), year)

        # test with "current" epoch
        epoch.data = self.epochs[-1].id

        # negative years are still invalid
        year.data = -1
        with self.assertRaises(ValidationError):
            ype(FakeForm([year, epoch]), year)

        year.data = 0
        with self.assertRaises(ValidationError):
            ype(FakeForm([year, epoch]), year)

        # current epoch has no upper limit for years
        year.data = 1337
        ype(FakeForm([year, epoch]), year)

        # invalid epoch
        epoch.data = 1000
        year.data = 1
        with self.assertRaises(ValidationError):
            ype(FakeForm([year, epoch]), year)

    def test_DayPerMonthValidator(self, app, client):
        from app.validators import DayPerMonthValidator
        self.set_up_users()
        self.set_up_months()

        dpm = DayPerMonthValidator("month")

        day = FakeField("day", 1)
        month = FakeField("month", self.months[0].id)

        # day 1 is ok for Month 1
        dpm(FakeForm([day, month]), day)

        # day 10 is ok for Month 1
        day.data = 10
        dpm(FakeForm([day, month]), day)

        # Month 1 only has 10 days
        day.data = 11
        with self.assertRaises(ValidationError):
            dpm(FakeForm([day, month]), day)

        # day -1 is never ok
        day.data = -1
        with self.assertRaises(ValidationError):
            dpm(FakeForm([day, month]), day)

        # day 0 is never ok
        day.data = 0
        with self.assertRaises(ValidationError):
            dpm(FakeForm([day, month]), day)

        # invalid month
        day.data = 1
        month.data = 1000
        with self.assertRaises(ValidationError):
            dpm(FakeForm([day, month]), day)

    def test_IsDMValidator(self, app, client):
        from app.validators import IsDMValidator
        self.set_up_users()
        self.set_up_characters()
        self.set_up_parties()
        self.set_up_campaigns()

        idm = IsDMValidator()

        # must always validate for admin
        self.login(client, self.admin)
        idm(None, FakeField("campaign", self.campaign1.id))
        idm(None, FakeField("campaign", self.campaign2.id))
        idm(None, FakeField("campaign", self.campaign3.id))

        # non existing campaign
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", 1000))

        # moderator is dm of campaign2
        self.login(client, self.moderator)
        idm(None, FakeField("campaign", self.campaign2.id))
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", self.campaign1.id))
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", self.campaign3.id))

        # user is dm of campaign3
        self.login(client, self.user)
        idm(None, FakeField("campaign", self.campaign3.id))
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", self.campaign1.id))
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", self.campaign2.id))

        # user2 is not a DM
        self.login(client, self.user2)
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", self.campaign1.id))
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", self.campaign2.id))
        with self.assertRaises(ValidationError):
            idm(None, FakeField("campaign", self.campaign3.id))

    def test_IsRandomTableValidator(self, app, client):
        from app.validators import IsRandomTableValidator
        self.set_up_users()
        self.set_up_random_tables()

        irt = IsRandomTableValidator()

        # id 4 does not exist
        with self.assertRaises(ValidationError):
            irt(None, FakeField("name", 4))

        irt(None, FakeField("name", 1))
        irt(None, FakeField("name", 2))
        irt(None, FakeField("name", 3))

    def test_IsValidDiceStringValidator(self, app, client):
        from app.validators import IsValidDiceStringValidator
        self.set_up_users()
        self.set_up_random_dice()

        ivds = IsValidDiceStringValidator()

        with self.assertRaises(ValidationError):
            ivds(None, FakeField("dice_string", "1d6dl1"))

        with self.assertRaises(ValidationError):
            ivds(None, FakeField("dice_string", ""))

        with self.assertRaises(ValidationError):
            ivds(None, FakeField("dice_string", "hello world"))

        ivds(None, FakeField("dice_string", self.dice_set1.dice_string))
        ivds(None, FakeField("dice_string", self.dice_set2.dice_string))
        ivds(None, FakeField("dice_string", self.dice_set3.dice_string))
