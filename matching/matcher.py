from dataclasses import dataclass

from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.graph.operational.export_graph import OperationalGraph
from matching.match_config import MatchConfig
from matching.matching_solution import MatchingSolution


@dataclass
class MatchInput:
    graph: OperationalGraph
    empty_board: EmptyDroneDeliveryBoard
    config: MatchConfig


class InvalidMatchInputException(Exception):
    pass



class Matcher:

    def __init__(self, match_input: MatchInput):
        self._match_input = match_input

        self._valid_input()

    def match(self) -> MatchingSolution:
        pass

    @property
    def match_input(self):
        return self._match_input

    def _valid_input(self):
        if self._match_input.empty_board.num_of_formations == 0:
            raise InvalidMatchInputException(f"Empty Board must has at least one formation")

        return True