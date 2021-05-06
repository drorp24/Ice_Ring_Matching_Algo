import unittest
from copy import deepcopy
from pathlib import Path
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.graph.operational.operational_graph import OperationalNode, OperationalEdgeAttribs, OperationalEdge, \
    OperationalGraph


class BasicGraphNodeTestCases(unittest.TestCase):
    temp_path = Path('matching/test/jsons/test_solver_config_1.json')

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(random=Random(100),
                                                                          amount={DeliveryRequest: 3})
        cls.example_node_delivery_request_0 = OperationalNode(internal_node=cls.dr_dataset_random[0])
        cls.example_node_delivery_request_1 = OperationalNode(internal_node=cls.dr_dataset_random[1])

        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(random=Random(100), amount=2)
        cls.example_node_drone_loading_dock = OperationalNode(internal_node=cls.dld_dataset_random[0])

        cls.example_op_edge_attribs = OperationalEdgeAttribs(cost=42, travel_time_min=42)

        cls.example_op_edge = OperationalEdge(start_node=cls.example_node_delivery_request_0,
                                              end_node=cls.example_node_delivery_request_1,
                                              attributes=cls.example_op_edge_attribs)

        cls.example_operational_graph = OperationalGraph()
        cls.example_operational_graph.add_operational_nodes([cls.example_node_delivery_request_0,
                                                             cls.example_node_delivery_request_1,
                                                             cls.example_node_drone_loading_dock])
        cls.example_operational_graph.add_operational_edges([cls.example_op_edge])

    @classmethod
    def tearDownClass(cls):
        cls.temp_path.unlink()

    def test_delivery_request_operational_node_to_dict(self):
        op_node_dict = self.example_node_delivery_request_0.__dict__()
        self.assertTrue('internal_node' in op_node_dict.keys())
        self.assertTrue(op_node_dict['__class__'] is OperationalNode.__name__)
        self.assertTrue(op_node_dict['internal_node']['__class__'] is DeliveryRequest.__name__)
        self.assertEqual(DeliveryRequest.dict_to_obj(op_node_dict['internal_node']),
                         self.example_node_delivery_request_0.internal_node)
        self.assertEqual(OperationalNode.dict_to_obj(op_node_dict), self.example_node_delivery_request_0)

    def test_drone_loading_dock_operational_node_to_dict(self):
        op_node_dict = self.example_node_drone_loading_dock.__dict__()
        self.assertTrue('internal_node' in op_node_dict.keys())
        self.assertTrue(op_node_dict['__class__'] is OperationalNode.__name__)
        self.assertTrue(op_node_dict['internal_node']['__class__'] is DroneLoadingDock.__name__)
        self.assertEqual(DroneLoadingDock.dict_to_obj(op_node_dict['internal_node']),
                         self.example_node_drone_loading_dock.internal_node)
        self.assertEqual(OperationalNode.dict_to_obj(op_node_dict), self.example_node_drone_loading_dock)

    def test_edge_attributes_is_equal_after_dict(self):
        op_edge_attribs_dict = self.example_op_edge_attribs.__dict__()
        self.assertTrue(op_edge_attribs_dict['__class__'] is OperationalEdgeAttribs.__name__)
        self.assertEqual(OperationalEdgeAttribs.dict_to_obj(op_edge_attribs_dict), self.example_op_edge_attribs)

    def test_operational_edge_is_equal_after_dict(self):
        example_operational_graph_dict = self.example_operational_graph.__dict__()
        self.assertTrue(example_operational_graph_dict['__class__'] is OperationalGraph.__name__)
        obj1 = OperationalGraph.dict_to_obj(example_operational_graph_dict)
        self.assertEqual(obj1, self.example_operational_graph)

    def test_operational_graph_is_jsonable(self):
        self.example_operational_graph.to_json(self.temp_path)
        operational_graph_from_json = OperationalGraph.from_json(self.temp_path)
        self.assertEqual(self.example_operational_graph, operational_graph_from_json)

    def test_operational_graph_deepcopy(self):
        graph_copy = deepcopy(self.example_operational_graph)
        self.assertEqual(self.example_operational_graph, graph_copy)
