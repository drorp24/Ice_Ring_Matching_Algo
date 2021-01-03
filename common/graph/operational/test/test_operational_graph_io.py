import unittest
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.graph.operational.operational_graph import OperationalNode, OperationalEdgeAttribs, OperationalEdge


class BasicGraphNodeTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(random=Random(100),
                                                                          amount={DeliveryRequest: 3})
        cls.example_node_delivery_request_0 = OperationalNode(internal_node=cls.dr_dataset_random[0])
        cls.example_node_delivery_request_1 = OperationalNode(internal_node=cls.dr_dataset_random[1])

        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(random=Random(100), amount=2)
        cls.example_node_drone_loading_dock = OperationalNode(internal_node=cls.dld_dataset_random[0])

        cls.example_op_edge_attribs = OperationalEdgeAttribs(42)

        cls.example_op_edge = OperationalEdge(start_node=cls.example_node_delivery_request_0,
                                              end_node=cls.example_node_delivery_request_1,
                                              attributes=OperationalEdgeAttribs(100))

    def test_delivery_request_operational_node_to_dict(self):
        op_node_dict = self.example_node_delivery_request_0.__dict__()
        self.assertTrue('internal_node' in op_node_dict.keys())
        self.assertTrue(op_node_dict['__class__'] is 'OperationalNode')
        self.assertTrue(op_node_dict['internal_node']['__class__'] is DeliveryRequest.__name__)
        self.assertEqual(DeliveryRequest.dict_to_obj(op_node_dict['internal_node']),
                         self.example_node_delivery_request_0.internal_node)
        self.assertEqual(OperationalNode.dict_to_obj(op_node_dict), self.example_node_delivery_request_0)

    def test_drone_loading_dock_operational_node_to_dict(self):
        op_node_dict = self.example_node_drone_loading_dock.__dict__()
        self.assertTrue('internal_node' in op_node_dict.keys())
        self.assertTrue(op_node_dict['__class__'] is 'OperationalNode')
        self.assertTrue(op_node_dict['internal_node']['__class__'] is DroneLoadingDock.__name__)
        self.assertEqual(DroneLoadingDock.dict_to_obj(op_node_dict['internal_node']),
                         self.example_node_drone_loading_dock.internal_node)
        self.assertEqual(OperationalNode.dict_to_obj(op_node_dict), self.example_node_drone_loading_dock)

    def test_edge_attributes_is_equal_after_dict(self):
        op_edge_attribs_dict = self.example_op_edge_attribs.__dict__()
        self.assertTrue(op_edge_attribs_dict['__class__'] is OperationalEdgeAttribs.__name__)
        self.assertEqual(OperationalEdgeAttribs.dict_to_obj(op_edge_attribs_dict), self.example_op_edge_attribs)

    def test_operational_edge_is_equal_after_dict(self):
        example_op_edge_dict = self.example_op_edge.__dict__()
        self.assertTrue(example_op_edge_dict['__class__'] is OperationalEdge.__name__)
        self.assertEqual(OperationalEdge.dict_to_obj(example_op_edge_dict), self.example_op_edge)
