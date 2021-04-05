from tests import BaseTestCase


class MapModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_maps()

    def test_get_nodes(self, app, client):
        self.set_up_map_nodes()

        self.login(client, self.admin)
        self.assertEqual(len(self.map2.get_nodes()), 0)
        nodes = self.map1.get_nodes()
        self.assertEqual(len(nodes), 4)
        self.assertFalse(self.map_node4 in nodes)
        self.assertFalse(self.map_node6 in nodes)

        self.login(client, self.moderator)
        self.assertEqual(len(self.map2.get_nodes()), 0)
        nodes = self.map1.get_nodes()
        self.assertEqual(len(nodes), 4)
        self.assertFalse(self.map_node2 in nodes)
        self.assertFalse(self.map_node6 in nodes)

        self.login(client, self.user)
        self.assertEqual(len(self.map2.get_nodes()), 0)
        nodes = self.map1.get_nodes()
        self.assertEqual(len(nodes), 4)
        self.assertFalse(self.map_node2 in nodes)
        self.assertFalse(self.map_node4 in nodes)

        self.login(client, self.user2)
        self.assertEqual(len(self.map2.get_nodes()), 0)
        nodes = self.map1.get_nodes()
        self.assertEqual(len(nodes), 3)
        self.assertFalse(self.map_node2 in nodes)
        self.assertFalse(self.map_node4 in nodes)
        self.assertFalse(self.map_node6 in nodes)

    def test_permissions(self, app, client):
        self.assertNotImplemented(self.map1.is_deletable_by_user)

        self.login(client, self.admin)
        self.assertTrue(self.map1.is_viewable_by_user())
        self.assertTrue(self.map1.is_editable_by_user())
        self.assertTrue(self.map1.is_hideable_by_user())

        self.assertTrue(self.map2.is_viewable_by_user())
        self.assertTrue(self.map2.is_editable_by_user())
        self.assertTrue(self.map2.is_hideable_by_user())

        self.login(client, self.moderator)
        self.assertTrue(self.map1.is_viewable_by_user())
        self.assertFalse(self.map1.is_editable_by_user())
        self.assertFalse(self.map1.is_hideable_by_user())

        self.assertFalse(self.map2.is_viewable_by_user())
        self.assertFalse(self.map2.is_editable_by_user())
        self.assertFalse(self.map2.is_hideable_by_user())

        self.login(client, self.user)
        self.assertTrue(self.map1.is_viewable_by_user())
        self.assertFalse(self.map1.is_editable_by_user())
        self.assertFalse(self.map1.is_hideable_by_user())

        self.assertFalse(self.map2.is_viewable_by_user())
        self.assertFalse(self.map2.is_editable_by_user())
        self.assertFalse(self.map2.is_hideable_by_user())

        self.login(client, self.user2)
        self.assertTrue(self.map1.is_viewable_by_user())
        self.assertFalse(self.map1.is_editable_by_user())
        self.assertFalse(self.map1.is_hideable_by_user())

        self.assertFalse(self.map2.is_viewable_by_user())
        self.assertFalse(self.map2.is_editable_by_user())
        self.assertFalse(self.map2.is_hideable_by_user())


class MapNodeModelTest(BaseTestCase):
    def setUp(self, app, client):
        super().setUp(app, client)

        self.set_up_users()
        self.set_up_maps()
        self.set_up_map_nodes()

    def test_permissions(self, app, client):
        ########
        # Admin
        ########
        # Owns Node 1 and 2
        self.login(client, self.admin)
        self.assertTrue(self.map_node1.is_viewable_by_user())
        self.assertTrue(self.map_node1.is_editable_by_user())
        self.assertTrue(self.map_node1.is_hideable_by_user())
        self.assertTrue(self.map_node1.is_deletable_by_user())

        self.assertTrue(self.map_node2.is_viewable_by_user())
        self.assertTrue(self.map_node2.is_editable_by_user())
        self.assertTrue(self.map_node2.is_hideable_by_user())
        self.assertTrue(self.map_node2.is_deletable_by_user())

        self.assertTrue(self.map_node3.is_viewable_by_user())
        self.assertTrue(self.map_node3.is_editable_by_user())
        self.assertTrue(self.map_node3.is_hideable_by_user())
        self.assertTrue(self.map_node3.is_deletable_by_user())

        self.assertFalse(self.map_node4.is_viewable_by_user())
        self.assertFalse(self.map_node4.is_editable_by_user())
        self.assertFalse(self.map_node4.is_hideable_by_user())
        self.assertFalse(self.map_node4.is_deletable_by_user())

        self.assertTrue(self.map_node5.is_viewable_by_user())
        self.assertTrue(self.map_node5.is_editable_by_user())
        self.assertTrue(self.map_node5.is_hideable_by_user())
        self.assertTrue(self.map_node5.is_deletable_by_user())

        self.assertFalse(self.map_node6.is_viewable_by_user())
        self.assertFalse(self.map_node6.is_editable_by_user())
        self.assertFalse(self.map_node6.is_hideable_by_user())
        self.assertFalse(self.map_node6.is_deletable_by_user())

        ########
        # Moderator
        ########
        # Owns Node 3 and 4
        self.login(client, self.moderator)
        self.assertTrue(self.map_node1.is_viewable_by_user())
        self.assertTrue(self.map_node1.is_editable_by_user())
        self.assertTrue(self.map_node1.is_hideable_by_user())
        self.assertTrue(self.map_node1.is_deletable_by_user())

        self.assertFalse(self.map_node2.is_viewable_by_user())
        self.assertFalse(self.map_node2.is_editable_by_user())
        self.assertFalse(self.map_node2.is_hideable_by_user())
        self.assertFalse(self.map_node2.is_deletable_by_user())

        self.assertTrue(self.map_node3.is_viewable_by_user())
        self.assertTrue(self.map_node3.is_editable_by_user())
        self.assertTrue(self.map_node3.is_hideable_by_user())
        self.assertTrue(self.map_node3.is_deletable_by_user())

        self.assertTrue(self.map_node4.is_viewable_by_user())
        self.assertTrue(self.map_node4.is_editable_by_user())
        self.assertTrue(self.map_node4.is_hideable_by_user())
        self.assertTrue(self.map_node4.is_deletable_by_user())

        self.assertTrue(self.map_node5.is_viewable_by_user())
        self.assertTrue(self.map_node5.is_editable_by_user())
        self.assertTrue(self.map_node5.is_hideable_by_user())
        self.assertTrue(self.map_node5.is_deletable_by_user())

        self.assertFalse(self.map_node6.is_viewable_by_user())
        self.assertFalse(self.map_node6.is_editable_by_user())
        self.assertFalse(self.map_node6.is_hideable_by_user())
        self.assertFalse(self.map_node6.is_deletable_by_user())

        ########
        # User
        ########
        # Owns Node 5 and 6
        self.login(client, self.user)
        self.assertTrue(self.map_node1.is_viewable_by_user())
        self.assertTrue(self.map_node1.is_editable_by_user())
        self.assertFalse(self.map_node1.is_hideable_by_user())
        self.assertFalse(self.map_node1.is_deletable_by_user())

        self.assertFalse(self.map_node2.is_viewable_by_user())
        self.assertFalse(self.map_node2.is_editable_by_user())
        self.assertFalse(self.map_node2.is_hideable_by_user())
        self.assertFalse(self.map_node2.is_deletable_by_user())

        self.assertTrue(self.map_node3.is_viewable_by_user())
        self.assertTrue(self.map_node3.is_editable_by_user())
        self.assertFalse(self.map_node3.is_hideable_by_user())
        self.assertFalse(self.map_node3.is_deletable_by_user())

        self.assertFalse(self.map_node4.is_viewable_by_user())
        self.assertFalse(self.map_node4.is_editable_by_user())
        self.assertFalse(self.map_node4.is_hideable_by_user())
        self.assertFalse(self.map_node4.is_deletable_by_user())

        self.assertTrue(self.map_node5.is_viewable_by_user())
        self.assertTrue(self.map_node5.is_editable_by_user())
        self.assertTrue(self.map_node5.is_hideable_by_user())
        self.assertTrue(self.map_node5.is_deletable_by_user())

        self.assertTrue(self.map_node6.is_viewable_by_user())
        self.assertTrue(self.map_node6.is_editable_by_user())
        self.assertTrue(self.map_node6.is_hideable_by_user())
        self.assertTrue(self.map_node6.is_deletable_by_user())

        ########
        # User2
        ########
        # Does not own any map_node
        self.login(client, self.user2)
        self.assertTrue(self.map_node1.is_viewable_by_user())
        self.assertTrue(self.map_node1.is_editable_by_user())
        self.assertFalse(self.map_node1.is_hideable_by_user())
        self.assertFalse(self.map_node1.is_deletable_by_user())

        self.assertFalse(self.map_node2.is_viewable_by_user())
        self.assertFalse(self.map_node2.is_editable_by_user())
        self.assertFalse(self.map_node2.is_hideable_by_user())
        self.assertFalse(self.map_node2.is_deletable_by_user())

        self.assertTrue(self.map_node3.is_viewable_by_user())
        self.assertTrue(self.map_node3.is_editable_by_user())
        self.assertFalse(self.map_node3.is_hideable_by_user())
        self.assertFalse(self.map_node3.is_deletable_by_user())

        self.assertFalse(self.map_node4.is_viewable_by_user())
        self.assertFalse(self.map_node4.is_editable_by_user())
        self.assertFalse(self.map_node4.is_hideable_by_user())
        self.assertFalse(self.map_node4.is_deletable_by_user())

        self.assertTrue(self.map_node5.is_viewable_by_user())
        self.assertTrue(self.map_node5.is_editable_by_user())
        self.assertFalse(self.map_node5.is_hideable_by_user())
        self.assertFalse(self.map_node5.is_deletable_by_user())

        self.assertFalse(self.map_node6.is_viewable_by_user())
        self.assertFalse(self.map_node6.is_editable_by_user())
        self.assertFalse(self.map_node6.is_hideable_by_user())
        self.assertFalse(self.map_node6.is_deletable_by_user())

    def test_permissions_invis_map(self, app, client):
        """
        Test permissions when the parent map is invisible
        """
        self.map1.is_visible = False
        self.commit()

        ########
        # Admin
        ########
        # Owns Node 1 and 2
        self.login(client, self.admin)
        self.assertTrue(self.map_node1.is_viewable_by_user())
        self.assertTrue(self.map_node1.is_editable_by_user())
        self.assertTrue(self.map_node1.is_hideable_by_user())
        self.assertTrue(self.map_node1.is_deletable_by_user())

        self.assertTrue(self.map_node2.is_viewable_by_user())
        self.assertTrue(self.map_node2.is_editable_by_user())
        self.assertTrue(self.map_node2.is_hideable_by_user())
        self.assertTrue(self.map_node2.is_deletable_by_user())

        self.assertTrue(self.map_node3.is_viewable_by_user())
        self.assertTrue(self.map_node3.is_editable_by_user())
        self.assertTrue(self.map_node3.is_hideable_by_user())
        self.assertTrue(self.map_node3.is_deletable_by_user())

        self.assertFalse(self.map_node4.is_viewable_by_user())
        self.assertFalse(self.map_node4.is_editable_by_user())
        self.assertFalse(self.map_node4.is_hideable_by_user())
        self.assertFalse(self.map_node4.is_deletable_by_user())

        self.assertTrue(self.map_node5.is_viewable_by_user())
        self.assertTrue(self.map_node5.is_editable_by_user())
        self.assertTrue(self.map_node5.is_hideable_by_user())
        self.assertTrue(self.map_node5.is_deletable_by_user())

        self.assertFalse(self.map_node6.is_viewable_by_user())
        self.assertFalse(self.map_node6.is_editable_by_user())
        self.assertFalse(self.map_node6.is_hideable_by_user())
        self.assertFalse(self.map_node6.is_deletable_by_user())

        ########
        # Moderator
        ########
        # Owns Node 3 and 4
        self.login(client, self.moderator)
        self.assertFalse(self.map_node1.is_viewable_by_user())
        self.assertFalse(self.map_node1.is_editable_by_user())
        self.assertFalse(self.map_node1.is_hideable_by_user())
        self.assertFalse(self.map_node1.is_deletable_by_user())

        self.assertFalse(self.map_node2.is_viewable_by_user())
        self.assertFalse(self.map_node2.is_editable_by_user())
        self.assertFalse(self.map_node2.is_hideable_by_user())
        self.assertFalse(self.map_node2.is_deletable_by_user())

        self.assertFalse(self.map_node3.is_viewable_by_user())
        self.assertFalse(self.map_node3.is_editable_by_user())
        self.assertFalse(self.map_node3.is_hideable_by_user())
        self.assertFalse(self.map_node3.is_deletable_by_user())

        self.assertFalse(self.map_node4.is_viewable_by_user())
        self.assertFalse(self.map_node4.is_editable_by_user())
        self.assertFalse(self.map_node4.is_hideable_by_user())
        self.assertFalse(self.map_node4.is_deletable_by_user())

        self.assertFalse(self.map_node5.is_viewable_by_user())
        self.assertFalse(self.map_node5.is_editable_by_user())
        self.assertFalse(self.map_node5.is_hideable_by_user())
        self.assertFalse(self.map_node5.is_deletable_by_user())

        self.assertFalse(self.map_node6.is_viewable_by_user())
        self.assertFalse(self.map_node6.is_editable_by_user())
        self.assertFalse(self.map_node6.is_hideable_by_user())
        self.assertFalse(self.map_node6.is_deletable_by_user())

        ########
        # User
        ########
        # Owns Node 5 and 6
        self.login(client, self.user)
        self.assertFalse(self.map_node1.is_viewable_by_user())
        self.assertFalse(self.map_node1.is_editable_by_user())
        self.assertFalse(self.map_node1.is_hideable_by_user())
        self.assertFalse(self.map_node1.is_deletable_by_user())

        self.assertFalse(self.map_node2.is_viewable_by_user())
        self.assertFalse(self.map_node2.is_editable_by_user())
        self.assertFalse(self.map_node2.is_hideable_by_user())
        self.assertFalse(self.map_node2.is_deletable_by_user())

        self.assertFalse(self.map_node3.is_viewable_by_user())
        self.assertFalse(self.map_node3.is_editable_by_user())
        self.assertFalse(self.map_node3.is_hideable_by_user())
        self.assertFalse(self.map_node3.is_deletable_by_user())

        self.assertFalse(self.map_node4.is_viewable_by_user())
        self.assertFalse(self.map_node4.is_editable_by_user())
        self.assertFalse(self.map_node4.is_hideable_by_user())
        self.assertFalse(self.map_node4.is_deletable_by_user())

        self.assertFalse(self.map_node5.is_viewable_by_user())
        self.assertFalse(self.map_node5.is_editable_by_user())
        self.assertFalse(self.map_node5.is_hideable_by_user())
        self.assertFalse(self.map_node5.is_deletable_by_user())

        self.assertFalse(self.map_node6.is_viewable_by_user())
        self.assertFalse(self.map_node6.is_editable_by_user())
        self.assertFalse(self.map_node6.is_hideable_by_user())
        self.assertFalse(self.map_node6.is_deletable_by_user())

        ########
        # User2
        ########
        # Does not own any map_node
        self.login(client, self.user2)
        self.assertFalse(self.map_node1.is_viewable_by_user())
        self.assertFalse(self.map_node1.is_editable_by_user())
        self.assertFalse(self.map_node1.is_hideable_by_user())
        self.assertFalse(self.map_node1.is_deletable_by_user())

        self.assertFalse(self.map_node2.is_viewable_by_user())
        self.assertFalse(self.map_node2.is_editable_by_user())
        self.assertFalse(self.map_node2.is_hideable_by_user())
        self.assertFalse(self.map_node2.is_deletable_by_user())

        self.assertFalse(self.map_node3.is_viewable_by_user())
        self.assertFalse(self.map_node3.is_editable_by_user())
        self.assertFalse(self.map_node3.is_hideable_by_user())
        self.assertFalse(self.map_node3.is_deletable_by_user())

        self.assertFalse(self.map_node4.is_viewable_by_user())
        self.assertFalse(self.map_node4.is_editable_by_user())
        self.assertFalse(self.map_node4.is_hideable_by_user())
        self.assertFalse(self.map_node4.is_deletable_by_user())

        self.assertFalse(self.map_node5.is_viewable_by_user())
        self.assertFalse(self.map_node5.is_editable_by_user())
        self.assertFalse(self.map_node5.is_hideable_by_user())
        self.assertFalse(self.map_node5.is_deletable_by_user())

        self.assertFalse(self.map_node6.is_viewable_by_user())
        self.assertFalse(self.map_node6.is_editable_by_user())
        self.assertFalse(self.map_node6.is_hideable_by_user())
        self.assertFalse(self.map_node6.is_deletable_by_user())


class MapNodeTypeModelTest(BaseTestCase):
    """
    Nothing to test here currently.
    """
