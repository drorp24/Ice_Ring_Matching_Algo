from common.entities.delivery_request import DeliveryRequest
from common.graph.operational.delivery_request_graph import OperationalGraph, OperationalEdge


def create_locally_connected_dr_graph(delivery_requests: [DeliveryRequest], max_dist_to_connect: float = 100.0):
    drg = OperationalGraph()
    edges = []
    drg.add_delivery_request_nodes(delivery_requests)
    for start_dr in delivery_requests:
        end_dr_options = calc_dr_within_radius(start_dr, delivery_requests, max_dist_to_connect)
        for end_dr in end_dr_options:
            edges.append(OperationalEdge(start_dr, end_dr))
    drg.add_delivery_request_edges(edges)
    return drg


def calc_dr_within_radius(target_dr: DeliveryRequest, drs: [DeliveryRequest], radius: float):
    target_point = target_dr.calc_centroid()
    return list(filter(lambda dr: 0 < target_point.calc_distance_to_point(dr.calc_centroid()) < radius, drs))
