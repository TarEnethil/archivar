import os
import tempfile
from tests import BaseTestCase, FakeFile
from flask import get_flashed_messages


class MapHelperTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_maps()
        self.set_up_map_nodes()

    def test_upload_node_icon(self, app, client):
        from app.map.helpers import upload_node_icon

        img = FakeFile(filename="test.jpg")
        img_fail = FakeFile(filename="test.jpg", upload_should_fail=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["MAPNODES_DIR"] = tmpdir

            success, filename, width, height = upload_node_icon(img)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))
            self.assertTrue(success)
            self.assertEqual(width, 325)
            self.assertEqual(height, 325)

            success, filename, width, height = upload_node_icon(img, filename="fixname.jpg")
            self.assertTrue(os.path.exists(os.path.join(tmpdir, filename)))
            self.assertTrue(success)
            self.assertEqual(width, 325)
            self.assertEqual(height, 325)

            client.get("/")
            # flash() (used in case of failure) needs a http context
            with client.session_transaction():
                success, filename, width, height = upload_node_icon(img_fail)
                self.assertFalse(os.path.exists(os.path.join(tmpdir, filename)))
                self.assertFalse(success)
                flashes = get_flashed_messages()
                self.assertEqual(len(flashes), 1)
                self.assertTrue("intentionally" in flashes[0])

    def test_delete_node_icon(self, app, client):
        from app.map.helpers import delete_node_icon

        img = FakeFile(filename="test.jpg")
        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["MAPNODES_DIR"] = tmpdir

            # copy file to tmpdir (fake upload)
            img.save(os.path.join(tmpdir, img.filename))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, img.filename)))

            delete_node_icon(img.filename)
            self.assertFalse(os.path.exists(os.path.join(tmpdir, img.filename)))

            client.get("/")
            # flash() (used in case of failure) needs a http context
            with client.session_transaction():
                delete_node_icon("certainly_does_not_exist.jpg")
                flashes = get_flashed_messages()
                self.assertEqual(len(flashes), 1)
                self.assertTrue("Could not delete old icon" in flashes[0])

    def test_gen_node_type_choices(self, app, client):
        from app.map.helpers import gen_node_type_choices

        self.assertEqual(len(gen_node_type_choices()), 1+2)  # choose + each category

    def test_gen_submap_choices(self, app, client):
        from app.map.helpers import gen_submap_choices

        self.login(client, self.admin)
        maps = gen_submap_choices()
        self.assertEqual(len(maps), 1+2)

        self.login(client, self.moderator)
        maps = gen_submap_choices()
        self.assertEqual(len(maps), 1+1)

        self.login(client, self.user)
        maps = gen_submap_choices()
        self.assertEqual(len(maps), 1+1)

        self.login(client, self.user2)
        maps = gen_submap_choices()
        self.assertEqual(len(maps), 1+1)

        # customize choice string
        maps = gen_submap_choices(zerochoice="custom string")
        self.assertEqual(maps[0][1], "custom string")

        # ensure map2 is in there
        maps = gen_submap_choices(ensure=self.map2)
        self.assertEqual(len(maps), 1+2)

    def test_get_nodes_by_wiki_id(self, app, client):
        from app.map.helpers import get_nodes_by_wiki_id

        self.set_up_wiki()

        self.login(client, self.admin)
        self.assertEqual(len(get_nodes_by_wiki_id(100)), 0)  # non existent
        self.assertEqual(len(get_nodes_by_wiki_id(self.wiki_entry6.id)), 0)  # no entry

        self.map_node1.wiki_entry_id = self.wiki_entry1.id
        self.map_node2.wiki_entry_id = self.wiki_entry1.id
        self.map_node3.wiki_entry_id = self.wiki_entry1.id
        self.map_node4.wiki_entry_id = self.wiki_entry1.id
        self.map_node5.wiki_entry_id = self.wiki_entry1.id
        self.map_node6.wiki_entry_id = self.wiki_entry1.id
        self.commit()

        nodes = get_nodes_by_wiki_id(self.wiki_entry1.id)
        self.assertEqual(len(nodes), 4)
        self.assertFalse(self.map_node4 in nodes)
        self.assertFalse(self.map_node6 in nodes)

        self.login(client, self.moderator)
        nodes = get_nodes_by_wiki_id(self.wiki_entry1.id)
        self.assertEqual(len(nodes), 4)
        self.assertFalse(self.map_node2 in nodes)
        self.assertFalse(self.map_node6 in nodes)

        self.login(client, self.user)
        nodes = get_nodes_by_wiki_id(self.wiki_entry1.id)
        self.assertEqual(len(nodes), 4)
        self.assertFalse(self.map_node2 in nodes)
        self.assertFalse(self.map_node4 in nodes)

        self.login(client, self.user2)
        nodes = get_nodes_by_wiki_id(self.wiki_entry1.id)
        self.assertEqual(len(nodes), 3)
        self.assertFalse(self.map_node2 in nodes)
        self.assertFalse(self.map_node4 in nodes)
        self.assertFalse(self.map_node6 in nodes)

    def test_map_changed(self, app, client):
        from datetime import datetime
        from app.map.helpers import map_changed

        map_changed(self.map1.id)
        now = datetime.utcnow()
        delta = now - self.map1.last_change

        self.assertTrue((delta.total_seconds() < 1.0))
