from pathlib import Path
from unittest import TestCase

from common.entities.base_entities.base_entity import JsonableBaseEntity
from matching.ortools.ortools_solver_config import ORToolsSolverConfig


class SolverConfigTestCase(TestCase):

    temp_path = Path('matching/test/jsons/test_solver_config_1.json')

    @classmethod
    def setUpClass(cls):
        cls.solver_config_obj = ORToolsSolverConfig(first_solution_strategy="path_cheapest_arc",
                                                    local_search_strategy="automatic", timeout_sec=30)

    @classmethod
    def tearDownClass(cls):
        cls.temp_path.unlink()

    def test_match_config_to_dict(self):
        config_dict = self.solver_config_obj.__dict__()
        expected_config_obj = ORToolsSolverConfig.dict_to_obj(config_dict)
        expected_config_dict = expected_config_obj.__dict__()
        self.assertEqual(config_dict, expected_config_dict)
        self.assertEqual(self.solver_config_obj, expected_config_obj)

    def test_match_config_from_json(self):
        self.solver_config_obj.to_json(Path('matching/test/jsons/test_solver_config_1.json'))
        expected_config_dict = JsonableBaseEntity.json_to_dict(Path('matching/test/jsons/test_solver_config_1.json'))
        expected_config_obj = ORToolsSolverConfig.dict_to_obj(expected_config_dict)
        self.assertEqual(self.solver_config_obj, expected_config_obj)
