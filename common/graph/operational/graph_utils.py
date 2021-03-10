from typing import List, Dict

import numpy as np

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.zone import Zone
from common.tools.clustering_alg import fit_k_means
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.operational.operational_drawer2d import add_operational_graph


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
