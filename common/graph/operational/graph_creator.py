import math
from math import ceil
from typing import List
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.temporal import Temporal
from common.graph.operational.operational_graph import OperationalGraph, OperationalEdge, OperationalEdgeAttribs, \
    OperationalNode
from geometry.utils import Localizable


def add_locally_connected_dr_graph(graph, dr_connection_options: [DeliveryRequest], max_cost_to_connect=math.inf):
    edges = []
    graph.add_delivery_requests(dr_connection_options)
    for start_dr in dr_connection_options:
        end_dr_options = calc_under_cost(dr_connection_options, start_dr, max_cost_to_connect)
        for end_dr in end_dr_options:
            if has_overlapping_time_window(start_dr, end_dr):
                cost = calc_cost(start_dr, end_dr)
                edges.append(OperationalEdge(OperationalNode(start_dr),
                                             OperationalNode(end_dr),
                                             OperationalEdgeAttribs(cost)))
    graph.add_operational_edges(edges)


def build_time_overlapping_dependent_connected_graph(graph: OperationalGraph):
    nodes = list(graph.nodes)
    for i, origin_node in enumerate(nodes):
        destinations = list(filter(lambda x: x != origin_node and has_overlapping_time_window(origin_node.internal_node,
                                                                                              x.internal_node),
                                   nodes[i:]))
        edges = list(map(lambda y:
                         OperationalEdge(origin_node, y,
                                         OperationalEdgeAttribs(
                                             calc_cost(origin_node.internal_node, y.internal_node))),
                         destinations)) + \
                list(map(lambda y: OperationalEdge(y, origin_node,
                                                   OperationalEdgeAttribs(
                                                       calc_cost(origin_node.internal_node, y.internal_node))),
                         destinations))
        graph.add_operational_edges(edges)


def build_fully_connected_graph(graph: OperationalGraph, factor: float=1.0):
    nodes = list(graph.nodes)
    for i, origin_node in enumerate(nodes):
        destinations = list(filter(lambda x: x != origin_node,
                                   nodes[i:]))
        edges = list(map(lambda y:
                         OperationalEdge(origin_node, y,
                                         OperationalEdgeAttribs(
                                             calc_cost(origin_node.internal_node, y.internal_node, factor))),
                         destinations)) + \
                list(map(lambda y: OperationalEdge(y, origin_node,
                                                   OperationalEdgeAttribs(
                                                       calc_cost(origin_node.internal_node, y.internal_node, factor))),
                         destinations))
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
                            OperationalEdgeAttribs(calc_cost(node_content_1, node_content_2))),
            OperationalEdge(OperationalNode(node_content_2), OperationalNode(node_content_1),
                            OperationalEdgeAttribs(calc_cost(node_content_2, node_content_1)))]


def has_overlapping_time_window(start: Temporal, end: Temporal):
    return start.time_window.overlaps(end.time_window)


def get_delivery_requests_from_graph(graph) -> [DeliveryRequest]:
    return [n.internal_node for n in graph.nodes if n.internal_type is DeliveryRequest]


def calc_under_cost(potential: [Localizable], start: Localizable, cost_thresh) -> List:
    return list(filter(lambda target: is_within_cost_range(start, target, max_cost=cost_thresh), potential))


def is_within_cost_range(start: Localizable, target: Localizable,
                         max_cost: float = 1.0, min_cost: float = 0.0) -> bool:
    return min_cost < calc_cost(start, target) <= max_cost


def calc_cost(start: Localizable, end: Localizable, factor: float=1.0) -> int:
    return ceil(start.calc_location().calc_distance_to_point(end.calc_location())*factor)
