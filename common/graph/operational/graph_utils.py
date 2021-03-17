from typing import List, Dict

import numpy as np

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.package_holder import PackageHolder
from common.entities.base_entities.temporal import Temporal
from common.entities.base_entities.zone import Zone
from common.graph.operational.operational_graph import OperationalNode
from common.tools.clustering_alg import fit_k_means
from geometry.utils import Localizable
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.operational.operational_drawer2d import add_operational_graph


def has_at_least_one_identical_package_type(ph_1: PackageHolder, ph_2: PackageHolder):
    return ph_1.has_at_least_one_identical(ph_2)


def has_overlapping_time_window(start: Temporal, end: Temporal):
    return start.time_window.overlaps(end.time_window)


def filter_nodes_with_at_least_one_identical_package_type(selected_node, optional_nodes, delivery_option_index) -> \
        List[OperationalNode]:
    return list(
        filter(lambda x: x != selected_node and
                         (
                                 isinstance(x.internal_node, DroneLoadingDock) or
                                 isinstance(selected_node.internal_node, DroneLoadingDock) or
                                 has_at_least_one_identical_package_type(
                                     selected_node.internal_node.delivery_options[delivery_option_index],
                                     x.internal_node.delivery_options[delivery_option_index])
                         ),
               optional_nodes))


def filter_nodes_with_time_overlapping(selected_node, optional_nodes) -> List[OperationalNode]:
    return list(filter(lambda x: x != selected_node
                                 and has_overlapping_time_window(selected_node.internal_node,
                                                                 x.internal_node),
                       optional_nodes))


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


def calc_travel_time_in_min(start: Localizable, end: Localizable, edge_travel_time_factor: float = 1.0) -> float:
    return calc_distance(end, start) * edge_travel_time_factor


def sort_delivery_requests_by_zone(delivery_requests: [DeliveryRequest], zones: [Zone]) -> Dict[
    int, List[DeliveryRequest]]:
    return {zone_index: [dr for dr in delivery_requests if dr.calc_location() in zone.region] for
            zone_index, zone in enumerate(zones)}

def split_delivery_requests_into_clusters(delivery_requests: List[DeliveryRequest], max_clusters: int = 10) -> \
        Dict[int, List[DeliveryRequest]]:
    best_fit = fit_k_means(data=_get_delivery_requests_locations(delivery_requests), max_clusters=max_clusters)

    return {center_label: [k for k, v in zip(delivery_requests, best_fit.labels) if v == center_label] for
            center_label, center in enumerate(best_fit.centers)}


def _get_delivery_requests_locations(delivery_requests) -> np.ndarray:
    return np.array(
        [[np.array(dr.calc_location().x), np.array(dr.calc_location().y)] for dr in delivery_requests])


def draw_operational_graph(og):
    d = create_drawer_2d()
    add_operational_graph(d, og)
    d.draw()
