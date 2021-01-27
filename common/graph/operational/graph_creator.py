import itertools
import math
from datetime import timedelta
from itertools import repeat
from typing import List

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.temporal import Temporal, TimeDeltaExtension
from common.entities.base_entities.zone import Zone
from common.graph.operational.graph_utils import sort_delivery_requests_by_zone, grouping_delivery_requests
from common.graph.operational.operational_graph import OperationalGraph, OperationalEdge, OperationalEdgeAttribs, \
    OperationalNode
from geometry.utils import Localizable


def create_grouped_dr_graph(delivery_requests: [DeliveryRequest], drone_loading_docks: [DroneLoadingDock],
                            zones: [Zone]) -> OperationalGraph:
    delivery_requests_by_zone = sort_delivery_requests_by_zone(delivery_requests, zones)

    delivery_requests_groups = list(itertools.chain.from_iterable((
        map(lambda item: list(grouping_delivery_requests(item[1]).values()), delivery_requests_by_zone.items()))))

    graph = OperationalGraph()
    list(map(add_locally_connected_dr_graph, repeat(graph), delivery_requests_groups))
    add_fully_connected_loading_docks(graph, drone_loading_docks)
    return graph


def add_locally_connected_dr_graph(graph, dr_connection_options: [DeliveryRequest],
                                   max_distance_to_connect_km=math.inf):
    edges = []
    graph.add_delivery_requests(dr_connection_options)
    for start_dr in dr_connection_options:
        end_dr_options = calc_under_distance(dr_connection_options, start_dr, max_distance_to_connect_km)
        for end_dr in end_dr_options:
            if has_overlapping_time_window(start_dr, end_dr):
                cost = calc_cost(start_dr, end_dr)
                travel_time = calc_travel_time(start_dr, end_dr)
                edges.append(OperationalEdge(OperationalNode(start_dr),
                                             OperationalNode(end_dr),
                                             OperationalEdgeAttribs(cost, travel_time)))
    graph.add_operational_edges(edges)


def _create_directed_from_edges(origin_node: OperationalNode, destinations: List[OperationalNode],
                                edge_cost_factor: float = 1.0, edge_travel_time_factor: float = 1.0) -> \
        List[OperationalEdge]:
    edges = list(map(lambda y:
                     OperationalEdge(origin_node, y,
                                     OperationalEdgeAttribs(
                                         calc_cost(origin_node.internal_node, y.internal_node,
                                                   edge_cost_factor),
                                         calc_travel_time(origin_node.internal_node, y.internal_node,
                                                          edge_travel_time_factor)
                                     )),
                     destinations)) + \
            list(map(lambda y: OperationalEdge(y, origin_node,
                                               OperationalEdgeAttribs(
                                                   calc_cost(origin_node.internal_node, y.internal_node,
                                                             edge_cost_factor),
                                                   calc_travel_time(origin_node.internal_node,
                                                                    y.internal_node, edge_travel_time_factor)
                                               )),
                     destinations))
    return edges


def build_time_overlapping_dependent_connected_graph(graph: OperationalGraph,
                                                     edge_cost_factor: float = 1.0,
                                                     edge_travel_time_factor: float = 1.0):
    nodes = list(graph.nodes)
    for i, origin_node in enumerate(nodes):
        destinations = list(filter(lambda x: x != origin_node and has_overlapping_time_window(origin_node.internal_node,
                                                                                              x.internal_node),
                                   nodes[i:]))
        edges = _create_directed_from_edges(origin_node, destinations, edge_cost_factor, edge_travel_time_factor)
        graph.add_operational_edges(edges)


def build_fully_connected_graph(graph: OperationalGraph,
                                edge_cost_factor: float = 1.0,
                                edge_travel_time_factor: float = 1.0):
    nodes = list(graph.nodes)
    for i, origin_node in enumerate(nodes):
        destinations = list(filter(lambda x: x != origin_node,
                                   nodes[i:]))
        edges = _create_directed_from_edges(origin_node, destinations, edge_cost_factor, edge_travel_time_factor)
        graph.add_operational_edges(edges)


def add_fully_connected_loading_docks(graph: OperationalGraph, drone_loading_docks: [DroneLoadingDock]):
    graph.add_operational_nodes([OperationalNode(dld) for dld in drone_loading_docks])
    dr_in_graph = get_delivery_requests_from_graph(graph)
    edges = []
    for dld in drone_loading_docks:
        for dr in dr_in_graph:
            if has_overlapping_time_window(dld, dr):
                edges += create_two_way_directed_edges(dld, dr)
    graph.add_operational_edges(edges)


def create_two_way_directed_edges(node_content_1, node_content_2) -> [OperationalEdge]:
    return [OperationalEdge(OperationalNode(node_content_1), OperationalNode(node_content_2),
                            OperationalEdgeAttribs(calc_cost(node_content_1, node_content_2),
                                                   calc_travel_time(node_content_1, node_content_2))),
            OperationalEdge(OperationalNode(node_content_2), OperationalNode(node_content_1),
                            OperationalEdgeAttribs(calc_cost(node_content_2, node_content_1),
                                                   calc_travel_time(node_content_1, node_content_2)))]


def has_overlapping_time_window(start: Temporal, end: Temporal):
    return start.time_window.overlaps(end.time_window)


def get_delivery_requests_from_graph(graph) -> [DeliveryRequest]:
    return [n.internal_node for n in graph.nodes if n.internal_type is DeliveryRequest]


def calc_under_distance(potential: [Localizable], start: Localizable, max_distance_km) -> List:
    return list(
        filter(lambda target: is_within_distance_range(start, target, max_distance_km=max_distance_km), potential))


def is_within_distance_range(start: Localizable, target: Localizable,
                             max_distance_km: float = 1.0, min_distance_km: float = 0.0) -> bool:
    return min_distance_km < calc_distance(start, target) <= max_distance_km


def calc_distance(start: Localizable, end: Localizable) -> float:
    return start.calc_location().calc_distance_to_point(end.calc_location())


def calc_cost(start: Localizable, end: Localizable, edge_cost_factor: float = 1.0) -> float:
    return calc_distance(end, start) * edge_cost_factor


def calc_travel_time(start: Localizable, end: Localizable, edge_travel_time_factor: float = 1.0) -> TimeDeltaExtension:
    return TimeDeltaExtension(time_delta=timedelta(
        minutes=calc_distance(end, start) * edge_travel_time_factor))
