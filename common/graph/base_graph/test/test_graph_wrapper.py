import unittest
from dataclasses import dataclass

from common.graph.base_graph.graph_factory import create_empty_directed_graph
from common.graph.base_graph.graph_wrapper import GraphNode, DirectedEdge, DirectedGraph


@dataclass
class TestObject:
    attribute1: str
    attribute2: float


class BasicGraphTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.node1 = GraphNode(TestObject('obj1', 1.8), attributes={'name': 'node1'})
        cls.node2 = GraphNode(TestObject('obj2', 1.1), attributes={'name': 'node2'})
        cls.node3 = GraphNode(TestObject('obj3', 0.2), attributes={'name': 'node3'})
        cls.edge_1_to_3 = DirectedEdge(cls.node1, cls.node3, attributes={'value': 100})
        cls.edge_1_to_3_b = DirectedEdge(cls.node1, cls.node3, attributes={'value': 80})

    def test_creation_of_empty_graph(self):
        local_graph = create_empty_directed_graph()
        self.assertEqual(local_graph.num_of_nodes, 0)
        self.assertEqual(local_graph.num_of_edges, 0)

    def test_adding_node_to_graph(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_nodes([self.node1, self.node2, self.node3])
        self.assertTrue(self.node1 in local_graph)
        self.assertTrue(self.node2 in local_graph)
        self.assertTrue(self.node3 in local_graph)
        self.assertEqual(local_graph.num_of_nodes, 3)
        self.assertEqual(local_graph.num_of_edges, 0)

    def test_only_one_edge_can_exist_from_start_to_end(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_nodes([self.node1, self.node2, self.node3])
        local_graph.add_edge(self.edge_1_to_3)
        local_graph.add_edge(self.edge_1_to_3_b)
        self.assertEqual(local_graph.num_of_edges, 1)

    def test_adding_edge_to_graph(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_nodes([self.node1, self.node2, self.node3])
        local_graph.add_edge(self.edge_1_to_3)
        local_graph.add_edge(self.edge_1_to_3_b)
        self.assertFalse(self.edge_1_to_3 in local_graph)
        self.assertTrue(self.edge_1_to_3_b in local_graph)

    def test_adding_edge_to_graph_without_nodes_automatically_adds_nodes(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_edge(self.edge_1_to_3)
        self.assertEqual(local_graph.num_of_nodes, 2)
        self.assertEqual(local_graph.num_of_edges, 1)

    def test_adding_nodes_which_already_exist(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_node(self.node1)
        local_graph.add_node(self.node1)
        local_graph.add_node(self.node1)
        self.assertEqual(local_graph.num_of_nodes, 1)

    def test_adding_edge_to_graph(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_nodes([self.node1, self.node2, self.node3])
        local_graph.add_edge(self.edge_1_to_3)
        self.assertEqual(local_graph.num_of_nodes, 3)
        self.assertEqual(local_graph.num_of_edges, 1)

    def test_removing_unconnected_node_from_graph(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_node(self.node1)
        local_graph.remove_node(self.node1)
        self.assertEqual(local_graph.num_of_nodes, 0)

    def test_removing_node_from_edge_in_graph(self):
        local_graph = create_empty_directed_graph()
        local_graph.add_edge(self.edge_1_to_3)
        local_graph.remove_node(self.node1)
        self.assertEqual(local_graph.num_of_nodes, 1)
        self.assertEqual(local_graph.num_of_edges, 0)
        self.assertTrue(self.node3 in local_graph)