import itertools
import math
from itertools import repeat
from typing import List

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.zone import Zone
from common.graph.operational.graph_utils import sort_delivery_requests_by_zone, split_delivery_requests_into_clusters, \
    get_delivery_requests_from_graph, has_overlapping_time_window, calc_travel_time_in_min, calc_cost, \
    calc_under_distance, filter_nodes_with_at_least_one_identical_package_type, \
    filter_nodes_with_time_overlapping, has_at_least_one_identical_package_type
from common.graph.operational.operational_graph import OperationalGraph, OperationalEdge, OperationalEdgeAttribs, \
    OperationalNode


def create_clustered_delivery_requests_graph(delivery_requests: [DeliveryRequest],
                                             drone_loading_docks: [DroneLoadingDock],
                                             zones: [Zone],
                                             edge_cost_factor: float = 1.0,
                                             edge_travel_time_factor: float = 1.0,
                                             max_clusters: int = 1
                                             ) -> OperationalGraph:
    delivery_requests_by_zone = sort_delivery_requests_by_zone(delivery_requests, zones)

    delivery_requests_clusters = list(itertools.chain.from_iterable((
        map(lambda item: list(
            split_delivery_requests_into_clusters(delivery_requests=item[1], max_clusters=max_clusters).values()),
            delivery_requests_by_zone.items()))))

    graph = OperationalGraph()
    list(map(add_locally_connected_dr_graph, repeat(graph), delivery_requests_clusters,
             repeat(edge_cost_factor),
             repeat(edge_travel_time_factor),
             repeat(math.inf)))
    add_fully_connected_loading_docks(graph, drone_loading_docks, edge_cost_factor, edge_travel_time_factor)

    return graph

def create_package_time_zones_dependent_graph_model(delivery_requests: [DeliveryRequest],
                                                    drone_loading_docks: [DroneLoadingDock],
                                                    zones: [Zone],
                                                    edge_cost_factor: float = 1.0,
                                                    edge_travel_time_factor: float = 1.0
                                                    ) -> OperationalGraph:
    delivery_requests_by_zone = sort_delivery_requests_by_zone(delivery_requests, zones)

    graph = OperationalGraph()
    list(map(add_locally_connected_dr_graph_packages_time_dependent, repeat(graph), delivery_requests_by_zone.values(),
             repeat(edge_cost_factor),
             repeat(edge_travel_time_factor),
             repeat(math.inf)))
    add_fully_connected_loading_docks(graph, drone_loading_docks, edge_cost_factor, edge_travel_time_factor)

    return graph


def add_locally_connected_dr_graph_packages_time_dependent(graph, dr_connection_options: [DeliveryRequest],
                                                           edge_cost_factor: float = 1.0,
                                                           edge_travel_time_factor: float = 1.0,
                                                           max_distance_to_connect_km=math.inf,
                                                           delivery_option_index: int = 0
                                                           ):
    edges = []
    graph.add_delivery_requests(dr_connection_options)
    for start_dr in dr_connection_options:
        end_dr_options = calc_under_distance(dr_connection_options, start_dr, max_distance_to_connect_km)
        for end_dr in end_dr_options:
            if has_overlapping_time_window(start_dr, end_dr) and has_at_least_one_identical_package_type(
                    start_dr.delivery_options[delivery_option_index], end_dr.delivery_options[delivery_option_index]):
                cost = calc_cost(start_dr, end_dr, edge_cost_factor)
                travel_time = calc_travel_time_in_min(start_dr, end_dr, edge_travel_time_factor)
                edges.append(OperationalEdge(OperationalNode(start_dr),
                                             OperationalNode(end_dr),
                                             OperationalEdgeAttribs(cost, travel_time)))
    graph.add_operational_edges(edges)

def add_locally_connected_dr_graph(graph, dr_connection_options: [DeliveryRequest],
                                   edge_cost_factor: float = 1.0,
                                   edge_travel_time_factor: float = 1.0,
                                   max_distance_to_connect_km=math.inf
                                   ):
    edges = []
    graph.add_delivery_requests(dr_connection_options)
    for start_dr in dr_connection_options:
        end_dr_options = calc_under_distance(dr_connection_options, start_dr, max_distance_to_connect_km)
        for end_dr in end_dr_options:
            if has_overlapping_time_window(start_dr, end_dr):
                cost = calc_cost(start_dr, end_dr, edge_cost_factor)
                travel_time = calc_travel_time_in_min(start_dr, end_dr, edge_travel_time_factor)
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
                                         calc_travel_time_in_min(origin_node.internal_node, y.internal_node,
                                                                 edge_travel_time_factor)
                                     )),
                     destinations)) + \
            list(map(lambda y: OperationalEdge(y, origin_node,
                                               OperationalEdgeAttribs(
                                                   calc_cost(origin_node.internal_node, y.internal_node,
                                                             edge_cost_factor),
                                                   calc_travel_time_in_min(origin_node.internal_node,
                                                                           y.internal_node, edge_travel_time_factor)
                                               )),
                     destinations))
    return edges


def build_time_overlapping_dependent_connected_graph(graph: OperationalGraph,
                                                     edge_cost_factor: float = 1.0,
                                                     edge_travel_time_factor: float = 1.0):
    nodes = list(graph.nodes)
    for selected_node_index, origin_node in enumerate(nodes):
        destinations = filter_nodes_with_time_overlapping(selected_node=origin_node,
                                                          optional_nodes=graph.nodes[selected_node_index:])
        edges = _create_directed_from_edges(origin_node, destinations, edge_cost_factor, edge_travel_time_factor)
        graph.add_operational_edges(edges)


def build_package_dependent_connected_graph(graph: OperationalGraph,
                                            edge_cost_factor: float = 1.0,
                                            edge_travel_time_factor: float = 1.0,
                                            delivery_option_index: int = 0):
    for selected_node_index, selected_node in enumerate(graph.nodes):
        destinations = filter_nodes_with_at_least_one_identical_package_type(selected_node=selected_node,
                                                                             optional_nodes=graph.nodes[
                                                                                            selected_node_index:],
                                                                             delivery_option_index=delivery_option_index)
        edges = _create_directed_from_edges(selected_node, destinations, edge_cost_factor, edge_travel_time_factor)
        graph.add_operational_edges(edges)


def build_package_time_dependent_connected_graph(graph: OperationalGraph,
                                                     edge_cost_factor: float = 1.0,
                                                     edge_travel_time_factor: float = 1.0,
                                                     delivery_option_index: int = 0):
    for selected_node_index, selected_node in enumerate(graph.nodes):
        destinations_by_packages = filter_nodes_with_at_least_one_identical_package_type(selected_node=selected_node,
                                                                                         optional_nodes=graph.nodes[
                                                                                                        selected_node_index:],
                                                                                         delivery_option_index=delivery_option_index)
        destinations_by_times = filter_nodes_with_time_overlapping(selected_node=selected_node,
                                                                   optional_nodes=graph.nodes[
                                                                                  selected_node_index:])

        destinations = list(set(destinations_by_packages).intersection(set(destinations_by_times)))

        edges = _create_directed_from_edges(selected_node, destinations, edge_cost_factor, edge_travel_time_factor)
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


def add_fully_connected_loading_docks(graph: OperationalGraph, drone_loading_docks: [DroneLoadingDock],
                                      edge_cost_factor: float = 1.0,
                                      edge_travel_time_factor: float = 1.0):
    graph.add_drone_loading_docks(drone_loading_docks)
    dr_in_graph = get_delivery_requests_from_graph(graph)
    edges = []
    for dld in drone_loading_docks:
        for dr in dr_in_graph:
            if has_overlapping_time_window(dld, dr):
                edges += create_two_way_directed_edges(dld, dr, edge_cost_factor, edge_travel_time_factor)
    graph.add_operational_edges(edges)


def create_two_way_directed_edges(node_content_1, node_content_2,
                                  edge_cost_factor: float = 1.0,
                                  edge_travel_time_factor: float = 1.0
                                  ) -> [OperationalEdge]:
    return [OperationalEdge(OperationalNode(node_content_1), OperationalNode(node_content_2),
                            OperationalEdgeAttribs(calc_cost(node_content_1, node_content_2, edge_cost_factor),
                                                   calc_travel_time_in_min(node_content_1, node_content_2,
                                                                           edge_travel_time_factor))),
            OperationalEdge(OperationalNode(node_content_2), OperationalNode(node_content_1),
                            OperationalEdgeAttribs(calc_cost(node_content_2, node_content_1, edge_cost_factor),
                                                   calc_travel_time_in_min(node_content_1, node_content_2,
                                                                           edge_travel_time_factor)))]
