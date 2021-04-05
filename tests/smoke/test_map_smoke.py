import os
import tempfile
from app.map.models import MapSetting
from flask import url_for
from tests import SmokeWrapper, FakeFile


class MapSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_maps()
        self.set_up_map_nodes()

        self.add(MapSetting(default_map=self.map1.id))
        self.commit()

    def tile_test(self, app, client):
        """
        test tile endpoint
        """
        img = FakeFile(filename="test.jpg")

        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["MAPTILES_DIR"] = tmpdir

            # copy image to fake upload folder
            img.save(os.path.join(tmpdir, img.filename))

            self.assertHTTPOK(client, url_for("map.tile", filename="test.jpg"), url=True)

    def set_up_common_urls(self):
        self.common_urls = [self.map1.view_url(),
                            url_for("map.view_with_node", id=self.map1.id, m_name="b",
                                    n_id=self.map_node1.id, n_name="a"),
                            url_for("map.last_change", id=self.map1.id)]
        self.common_endpoints = ["map.list"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "map.index", follow=True)
        self.assertHTTPOK(client, "map.create")
        self.assertHTTPOK(client, "map.settings")

        self.assertHTTPOK(client, url_for("map.view", id=self.map2.id, name="a"), url=True)
        self.assertHTTPOK(client, url_for("map.map_settings", id=self.map2.id, name="b"), url=True)

        self.tile_test(app, client)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, "map.index", follow=True)
        self.tile_test(app, client)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, "map.index", follow=True)
        self.tile_test(app, client)


class MapNodeSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_maps()
        self.set_up_map_nodes()

        self.add(MapSetting(default_map=self.map1.id))
        # json endpoint panics otherwise (encode of None-obj)
        self.map_node1.description = ""
        self.map_node2.description = ""
        self.map_node3.description = ""
        self.map_node4.description = ""
        self.map_node5.description = ""
        self.map_node6.description = ""
        self.commit()

    def set_up_common_urls(self):
        self.common_urls = [url_for("map.node_create", map_id=self.map1.id, x=0, y=0),
                            url_for("map.node_edit", id=self.map_node1.id),
                            url_for("map.node_edit", id=self.map_node3.id),
                            url_for("map.node_edit", id=self.map_node5.id),
                            url_for("map.node_json", id=self.map1.id)]
        self.common_endpoints = None

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.map_node2.on_map = self.map2.id
        self.commit()

        self.assertHTTPOK(client, url_for("map.node_create", map_id=self.map2.id, x=0, y=0), url=True)
        self.assertHTTPOK(client, url_for("map.node_edit", id=self.map_node2.id), url=True)

        self.assertHTTPOK(client, url_for("map.node_delete", id=self.map_node1.id), url=True, get=False)
        self.assertHTTPOK(client, url_for("map.node_delete", id=self.map_node2.id), url=True, get=False)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, url_for("map.node_edit", id=self.map_node4.id), url=True)

        self.assertHTTPOK(client, url_for("map.node_delete", id=self.map_node3.id), url=True, get=False)
        self.assertHTTPOK(client, url_for("map.node_delete", id=self.map_node4.id), url=True, get=False)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.assertHTTPOK(client, url_for("map.node_edit", id=self.map_node6.id), url=True)

        self.assertHTTPOK(client, url_for("map.node_delete", id=self.map_node5.id), url=True, get=False)
        self.assertHTTPOK(client, url_for("map.node_delete", id=self.map_node6.id), url=True, get=False)


class MapNodeTypeSmokeTest(SmokeWrapper.SmokeTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_maps()
        self.set_up_map_nodes()

        self.add(MapSetting(default_map=self.map1.id))
        self.commit()

    def icon_test(self, app, client):
        """
       test node type icon endpoint
        """
        img = FakeFile(filename="test.jpg")

        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["MAPNODES_DIR"] = tmpdir

            # copy image to fake upload folder
            img.save(os.path.join(tmpdir, img.filename))

            self.assertHTTPOK(client, url_for("map.node_type_icon", filename="test.jpg"), url=True)

    def set_up_common_urls(self):
        self.common_urls = None
        self.common_endpoints = ["map.node_type_json"]

    def test_reachability_admin(self, app, client):
        self.login(client, self.admin)

        self.assertHTTPOK(client, "map.node_type_create")
        self.assertHTTPOK(client, url_for("map.node_type_edit", id=self.map_node_type1.id), url=True)
        self.assertHTTPOK(client, url_for("map.node_type_edit", id=self.map_node_type2.id), url=True)

        self.icon_test(app, client)

    def test_reachability_moderator(self, app, client):
        self.login(client, self.moderator)

        self.assertHTTPOK(client, "map.node_type_create")
        self.assertHTTPOK(client, url_for("map.node_type_edit", id=self.map_node_type1.id), url=True)
        self.assertHTTPOK(client, url_for("map.node_type_edit", id=self.map_node_type2.id), url=True)

        self.icon_test(app, client)

    def test_reachability_user(self, app, client):
        self.login(client, self.user)

        self.icon_test(app, client)
