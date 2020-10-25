import unittest
from dataclasses import dataclass

from common.graph.base_graph.graph_factory import create_empty_directed_graph
from common.graph.base_graph.graph_wrapper import GraphNode, DirectedEdge


@dataclass
class TestObject:
    attribute1: str
    attribute2: float


class BasicGraphTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.graph = create_empty_directed_graph()
        cls.node1 = GraphNode(TestObject('obj1', 1.8), attributes={'name': 'node1'})
        cls.node2 = GraphNode(TestObject('obj2', 1.1), attributes={'name': 'node2'})
        cls.node3 = GraphNode(TestObject('obj3', 0.2), attributes={'name': 'node3'})
        cls.edge_1_to_3 = DirectedEdge(cls.node1, cls.node3, attributes={'value': 100})
        cls.edge_1_to_3_b = DirectedEdge(cls.node1, cls.node3, attributes={'value': 80})

    def test_creation_of_empty_graph(self):
        self.assertEqual(self.graph.num_of_nodes, 0)
        self.assertEqual(self.graph.num_of_edges, 0)

    def test_adding_node_to_graph(self):
        self.add_setup_nodes_to_graph()
        self.assertTrue(self.node1 in self.graph)
        self.assertTrue(self.node2 in self.graph)
        self.assertTrue(self.node3 in self.graph)
        self.assertEqual(self.graph.num_of_nodes, 3)
        self.assertEqual(self.graph.num_of_edges, 0)

    def test_only_one_edge_can_exist_from_start_to_end(self):
        self.add_setup_nodes_to_graph()
        self.graph.add_edge(self.edge_1_to_3)
        self.graph.add_edge(self.edge_1_to_3_b)
        self.assertEqual(self.graph.num_of_edges, 1)

    def test_adding_edge_to_graph(self):
        self.add_setup_nodes_to_graph()
        self.graph.add_edge(self.edge_1_to_3)
        self.graph.add_edge(self.edge_1_to_3_b)
        self.assertFalse(self.edge_1_to_3 in self.graph)
        self.assertTrue(self.edge_1_to_3_b in self.graph)

    def test_adding_edge_to_graph_without_nodes_automatically_adds_nodes(self):
        self.graph.add_edge(self.edge_1_to_3)
        self.assertEqual(self.graph.num_of_nodes, 2)
        self.assertEqual(self.graph.num_of_edges, 1)

    def test_all_nodes_are_unique_otherwise_they_are_not_added(self):
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.assertEqual(self.graph.num_of_nodes, 1)

    def test_adding_edge_to_graph(self):
        self.add_setup_nodes_to_graph()
        self.graph.add_edge(self.edge_1_to_3)
        self.assertEqual(self.graph.num_of_nodes, 3)
        self.assertEqual(self.graph.num_of_edges, 1)

    def test_removing_node_from_graph(self):
        self.add_setup_nodes_to_graph()

    def add_setup_nodes_to_graph(self):
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_node(self.node3)