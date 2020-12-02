from datetime import date, time
from pathlib import Path
from unittest import TestCase

from common.entities.base_entity import JsonableBaseEntity
from common.entities.temporal import DateTimeExtension
from matching.match_config import MatchConfig, MatchConfigProperties, MatchSolver, MatchConstraints, \
    PriorityConstraints, TimeConstraints, CapacityConstraints


class MatchConfigTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.match_config_properties = MatchConfigProperties(
            zero_time=DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)),
            first_solution_strategy="or_tools:path_cheapest_arc",
            solver=MatchSolver(full_name="or_tools:automatic", timeout_sec=30),
            match_constraints=MatchConstraints(capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                                               time_constraints=TimeConstraints(waiting_time_allowed_min=10,
                                                                                max_total_drone_time_min=300,
                                                                                count_time_from_zero=False),
                                               priority_constraints=PriorityConstraints(True)),
            dropped_penalty=5)

        cls.config_obj = MatchConfig(match_config_properties=cls.match_config_properties)

    def test_match_config_to_dict(self):
        config_dict = self.config_obj.__dict__()

        expected_config_obj = MatchConfig.dict_to_obj(config_dict)
        expected_config_dict = expected_config_obj.__dict__()

        self.assertEqual(config_dict, expected_config_dict)
        self.assertEqual(self.config_obj, expected_config_obj)

    def test_match_config_from_json(self):
        expected_config_dict = JsonableBaseEntity.json_to_dict(Path('matching/test/match_config1.json'))
        expected_config_obj = MatchConfig.dict_to_obj(expected_config_dict)

        self.assertEqual(self.config_obj, expected_config_obj)
