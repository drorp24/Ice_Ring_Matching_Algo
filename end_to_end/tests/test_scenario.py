import unittest
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from end_to_end.scenario import ScenarioDistribution, Scenario


class BasicScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = ScenarioDistribution().choose_rand(random=Random(), amount={DeliveryRequest: 10, DroneLoadingDock: 1})[0]

    def test_scenario_amounts(self):
        self.assertEqual(len(self.scenario.delivery_requests), 10)
        self.assertEqual(len(self.scenario.drone_loading_docks), 1)

