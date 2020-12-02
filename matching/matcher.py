import enum
import json
from dataclasses import dataclass
from pathlib import Path
from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.temporal import DateTimeExtension
from common.graph.operational.export_graph import OperationalGraph
from matching.match_config import MatchConfig
from matching.matching_solution import MatchingSolution


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
