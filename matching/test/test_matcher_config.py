from datetime import date, time
from pathlib import Path
from unittest import TestCase

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.temporal import DateTimeExtension
from matching.constraint_config import CapacityConstraints, TimeConstraints, PriorityConstraints
from matching.matcher_config import ConstraintsConfig, MatcherConfig
from matching.matcher_factory import SolverVendor
from matching.monitor_config import MonitorConfig
from matching.ortools.ortools_solver_config import ORToolsSolverConfig


class MatchConfigTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_obj = MatcherConfig(
            zero_time=DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)),
            solver=ORToolsSolverConfig(SolverVendor.OR_TOOLS, first_solution_strategy="path_cheapest_arc",
                                local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=10,
                                                 max_route_time=300,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            unmatched_penalty=5,
        monitor=MonitorConfig(enabled=False))

    def test_match_config_to_dict(self):
        config_dict = self.config_obj.__dict__()
        expected_config_obj = MatcherConfig.dict_to_obj(config_dict)
        expected_config_dict = expected_config_obj.__dict__()
        self.assertEqual(config_dict, expected_config_dict)
        self.assertEqual(self.config_obj, expected_config_obj)

    def test_match_config_from_json(self):
        expected_config_dict = JsonableBaseEntity.json_to_dict(Path('matching/test/jsons/test_matcher_config_1.json'))
        expected_config_obj = MatcherConfig.dict_to_obj(expected_config_dict)

        self.assertEqual(self.config_obj, expected_config_obj)
