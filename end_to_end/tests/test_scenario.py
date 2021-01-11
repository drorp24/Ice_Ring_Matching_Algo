import unittest
from pathlib import Path
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from end_to_end.distribution.scenario_distribution import ScenarioDistribution
from end_to_end.scenario import  Scenario


class BasicScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = ScenarioDistribution().choose_rand(random=Random(), amount={DeliveryRequest: 10, DroneLoadingDock: 1})

    def test_scenario_amounts(self):
        self.assertEqual(len(self.scenario.delivery_requests), 10)
        self.assertEqual(len(self.scenario.drone_loading_docks), 1)

    def test_writing_scenario(self):
        test_json_file_name = Path('end_to_end/tests/jsons/test_writing_scenario.json')
        self.scenario.to_json(test_json_file_name)
        loaded_scenario_dict = Scenario.json_to_dict(test_json_file_name)
        loaded_scenario = self.scenario.dict_to_obj(loaded_scenario_dict)
        self.assertEqual(self.scenario.zero_time, loaded_scenario.zero_time)
        self.assertEqual(self.scenario.drone_loading_docks, loaded_scenario.drone_loading_docks)
        self.assertEqual(self.scenario.delivery_requests, loaded_scenario.delivery_requests)