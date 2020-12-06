import unittest
from pathlib import Path

from end_to_end.minimum_end_to_end import MinimumEnd2EndConfig


class BasicMinimumConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jsons_dir = 'end_to_end/tests/jsons'
        cls.config_file_path = Path(cls.jsons_dir, 'test_config.json')
        cls.scenario_file_path = Path(cls.jsons_dir, 'test_scenario.json')
        cls.fleet_file_path = Path(cls.jsons_dir, 'test_fleet.json')
        cls.matcher_file_path = Path(cls.jsons_dir, 'test_matcher_config.json')
        cls.config = MinimumEnd2EndConfig(cls.scenario_file_path, cls.fleet_file_path, cls.matcher_file_path)

    def test_config_file_exist(self):
        self.config.to_json(self.config_file_path)
        self.assertTrue(self.config_file_path.exists())

    def test_config_file_read(self):
        config_dict = MinimumEnd2EndConfig.json_to_dict(self.config_file_path)
        loaded_config = MinimumEnd2EndConfig.dict_to_obj(config_dict)
        self.assertEqual(loaded_config.matcher_config_json, str(self.matcher_file_path))
        self.assertEqual(loaded_config.fleet_partition_json, str(self.fleet_file_path))
        self.assertEqual(loaded_config.scenario_json, str(self.scenario_file_path))

