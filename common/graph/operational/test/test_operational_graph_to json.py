import unittest
from random import Random

from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.graph.operational.operational_graph import OperationalNode


class OperationalNodeJsonTestCase(unittest.TestCase):

    def setUpClass(cls) -> None:
        dr = DeliveryRequestDistribution.choose_rand(random=Random(42))[0]
        cls.node = OperationalNode(dr)

    def test_operational_node_json(self):
        self.assertTrue(self.node is OperationalNode)

    def test_abcd(self):
        pass