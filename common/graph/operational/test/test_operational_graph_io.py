import unittest
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.graph.operational.operational_graph import OperationalNode, NonLocalizableNodeException


class BasicGraphNodeTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(random=Random(100),
                                                                          amount={DeliveryRequest: 10})
        cls.example_node = OperationalNode(internal_node=cls.dr_dataset_random[0])

    def test_localizable_node_exception(self):
        op_node_dict = self.example_node.__dict__()
        self.assertTrue('internal_node' in op_node_dict.keys())
        self.assertTrue(op_node_dict['__class__'] is 'OperationalNode')
