from math import ceil
from typing import List

from common.entities.delivery_request import DeliveryRequest
from common.graph.operational.delivery_request_graph import OperationalGraph, OperationalEdge, OperationalEdgeAttributes


def create_locally_connected_dr_graph(dr_connection_options: [DeliveryRequest], max_cost_to_connect):
    drg = OperationalGraph()
    edges = []
    drg.add_operational_nodes(dr_connection_options)
    for start_dr in dr_connection_options:
        end_dr_options = calc_under_cost(dr_connection_options, start_dr, max_cost_to_connect)
        for end_dr in end_dr_options:
            cost = calc_discrete_cost(start_dr, end_dr)
            edges.append(OperationalEdge(start_dr, end_dr, OperationalEdgeAttributes(cost)))
    drg.add_operational_edges(edges)
    return drg


def calc_under_cost(potential_drs: [DeliveryRequest], start_dr: DeliveryRequest, cost_thresh) -> List:
    return list(filter(lambda target_dr: is_within_cost_range(start_dr, target_dr, max_cost=cost_thresh), potential_drs))


def is_within_cost_range(start_dr: DeliveryRequest, target_dr: DeliveryRequest,
                         max_cost: float = 1.0, min_cost: float = 0.0) -> bool:
    return min_cost < calc_discrete_cost(start_dr, target_dr) <= max_cost


def calc_discrete_cost(start_dr: DeliveryRequest, end_dr: DeliveryRequest) -> int:
    return ceil(start_dr.calc_centroid().calc_distance_to_point(end_dr.calc_centroid()))
