from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.graph.operational.graph_creator import *
from end_to_end.scenario import Scenario
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


def create_fully_connected_graph_model(scenario: Scenario, factor: float=1.0) -> OperationalGraph:
    operational_graph = OperationalGraph()
    operational_graph.add_drone_loading_docks(scenario.drone_loading_docks)
    operational_graph.add_delivery_requests(scenario.delivery_requests)
    build_time_overlapping_dependent_connected_graph(operational_graph, factor)
    return operational_graph


def calc_assignment(matcher_input: MatcherInput) -> DroneDeliveryBoard:
    matcher = create_matcher(matcher_input)
    return matcher.match()
