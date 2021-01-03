import unittest
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.graph.operational.operational_graph import OperationalNode


class BasicGraphNodeTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(random=Random(100),
                                                                          amount={DeliveryRequest: 3})
        cls.example_node_delivery_request = OperationalNode(internal_node=cls.dr_dataset_random[0])

        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(random=Random(100), amount=2)
        cls.example_node_drone_loading_dock = OperationalNode(internal_node=cls.dld_dataset_random[0])

    def test_delivery_request_operational_node_to_dict(self):
        op_node_dict = self.example_node_delivery_request.__dict__()
        self.assertTrue('internal_node' in op_node_dict.keys())
        self.assertTrue(op_node_dict['__class__'] is 'OperationalNode')
        self.assertTrue(op_node_dict['internal_node']['__class__'] is 'DeliveryRequest')
        self.assertTrue(DeliveryRequest.dict_to_obj(op_node_dict['internal_node']),
                        self.example_node_delivery_request.internal_node)

    def test_drone_loading_dock_operational_node_to_dict(self):
        op_node_dict = self.example_node_drone_loading_dock.__dict__()
        self.assertTrue('internal_node' in op_node_dict.keys())
        self.assertTrue(op_node_dict['__class__'] is 'OperationalNode')
        self.assertTrue(op_node_dict['internal_node']['__class__'] is 'DroneLoadingDock')
        self.assertTrue(DroneLoadingDock.dict_to_obj(op_node_dict['internal_node']),
                        self.example_node_drone_loading_dock.internal_node)
