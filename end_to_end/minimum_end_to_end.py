from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.graph.operational.graph_creator import *
from end_to_end.supplier_category import SupplierCategory
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


def create_fully_connected_graph_model(supplier_category: SupplierCategory, edge_cost_factor: float=1.0) -> OperationalGraph:
    operational_graph = OperationalGraph()
    operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
    operational_graph.add_delivery_requests(supplier_category.delivery_requests)
    build_time_overlapping_dependent_connected_graph(operational_graph, edge_cost_factor)
    return operational_graph


def calc_assignment(matcher_input: MatcherInput) -> DroneDeliveryBoard:
    matcher = create_matcher(matcher_input)
    return matcher.match()
