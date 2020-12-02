import unittest
from random import Random

from end_to_end.scenario import ScenarioDistribution, Scenario


class BasicScenario(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = ScenarioDistribution().choose_rand(random=Random(), amount=10, dock_amount=1)

    def test_scenario_amounts(self):
        self.assertEqual(len(self.scenario.delivery_requests), 10)
        self.assertEqual(len(self.scenario.drone_loading_docks), 1)

    def test_writing_json(self):
        scenario_json_path = 'end_to_end/tests/jsons/test_scenario.json'
        self.scenario.to_json(scenario_json_path)
        loaded_scenario_dict = Scenario.json_to_dict(scenario_json_path)
        loaded_scenario = Scenario.dict_to_obj(loaded_scenario_dict)
        self.assertEqual(loaded_scenario.drone_loading_docks, self.scenario.drone_loading_docks)

