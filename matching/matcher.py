import enum
import json
from dataclasses import dataclass
from pathlib import Path
from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.temporal import DateTimeExtension
from common.graph.operational.export_graph import OperationalGraph
from matching.matching_solution import MatchingSolution


class GraphDataType(enum.Enum):
    time_matrix = 'time_matrix'
    time_windows = 'time_windows'
    locations = 'locations'
    demands = 'demands'
    vehicle_capacities = 'vehicle_capacities'
    num_vehicles = 'num_vehicles'
    depot_ids = 'depot_ids'


class MatchConfigDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    @staticmethod
    def object_hook(dct):
        if 'match_config' in dct:
            return MatchConfig(dct['match_config'])
        return dct


class MatchConfig:
    def __init__(self, match_config_dict):
        self._zero_time = DateTimeExtension.from_dict(match_config_dict['zero_time'])
        self._solver = str.upper(match_config_dict['solver_name'].partition(':')[2])
        self._dropped_penalty = match_config_dict['dropped_penalty']
        self._waiting_time_allowed_min = match_config_dict['waiting_time_allowed_min']
        self._max_total_drone_time_min = match_config_dict['max_total_drone_time_min']
        self._count_time_from_zero = match_config_dict['count_time_from_zero']
        self._count_capacity_from_zero = match_config_dict['count_capacity_from_zero']
        self._count_priority_from_zero = match_config_dict['count_priority_from_zero']
        self._first_solution_strategy = match_config_dict['first_solution_strategy']
        self._time_limit_sec = match_config_dict['time_limit_sec']

    @classmethod
    def from_file(cls, file_path: Path) -> 'MatchConfig':
        with open(file_path, "r") as file:
            json_str = file.read()
        return json.loads(json_str, cls=MatchConfigDecoder)

    @classmethod
    def from_json(cls, json_str: str) -> 'MatchConfig':
        return json.loads(json_str, cls=MatchConfigDecoder)

    @property
    def solver(self):
        return self._solver

    @property
    def dropped_penalty(self):
        return self._dropped_penalty

    @property
    def waiting_time_allowed_min(self):
        return self._waiting_time_allowed_min

    @property
    def max_total_drone_time_min(self):
        return self._max_total_drone_time_min

    @property
    def count_time_from_zero(self):
        return self._count_time_from_zero

    @property
    def count_capacity_from_zero(self):
        return self._count_capacity_from_zero

    @property
    def count_priority_from_zero(self):
        return self._count_priority_from_zero

    @property
    def first_solution_strategy(self):
        return self._first_solution_strategy

    @property
    def time_limit_sec(self):
        return self._time_limit_sec

    @property
    def zero_time(self) -> DateTimeExtension:
        return self._zero_time


@dataclass
class MatchInput:
    graph: OperationalGraph
    empty_board: EmptyDroneDeliveryBoard
    config: MatchConfig


class Matcher:

    def __init__(self, match_input: MatchInput):
        self._input = match_input

    def match(self) -> MatchingSolution:
        pass

    @property
    def input(self):
        return self._input

    def _set_manager(self):
        pass

    def _set_routing(self):
        pass

    def _add_dropped_penalty(self, dropped_penalty):
        pass

    def _add_demand_constraints(self, constraints):
        pass

    def _add_time_constraints(self, constraints):
        pass

    def _set_parameters(self, diagnose_conf, selected_solver):
        pass

    def _solve(self):
        pass

    def _time_callback(self, from_index, to_index):
        """Returns the travel time between the two nodes."""
        pass

    def _demand_callback(self, from_index):
        """Returns the demand of the node."""
        pass
