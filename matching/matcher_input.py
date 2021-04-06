from dataclasses import dataclass

from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard
from common.graph.operational.operational_graph import OperationalGraph
from matching.matcher_config import MatcherConfig


@dataclass
class MatcherInput:
    graph: OperationalGraph
    empty_board: DeliveringDronesBoard
    config: MatcherConfig
