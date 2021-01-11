import sys
from functools import lru_cache
from typing import Tuple, List

import numpy as np

from common.entities.base_entities.package import PackageType
from common.graph.operational.export_graph import GraphExporter, OperationalGraph
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.temporal import DateTimeExtension


class OrtoolsGraphExporter(GraphExporter):

    def export_time_windows(self, graph: OperationalGraph, zero_time: DateTimeExtension) -> List[Tuple[int, int]]:
        nodes = graph.nodes
        time_windows = [tuple(map(int, node.time_window.get_relative_time_in_min(zero_time)))
                        for node in nodes]
        return time_windows

    @lru_cache()
    def export_priorities(self, graph: OperationalGraph) -> List[int]:
        nodes = list(graph.nodes)
        priorities = [node.priority for node in nodes]
        return priorities

    def export_travel_times(self, graph: OperationalGraph) -> np.ndarray:
        nodes = list(graph.nodes)
        edges = list(graph.edges)
        travel_times = np.full((len(nodes), (len(nodes))), sys.maxsize)
        for i in range(len(nodes)):
            travel_times[i, i] = 0
        for edge in edges:
            origin_idx = nodes.index(edge.start_node)
            destination_idx = nodes.index(edge.end_node)
            travel_times[origin_idx, destination_idx] = edge.attributes.cost
        return travel_times

    def export_basis_nodes_indices(self, graph: OperationalGraph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DroneLoadingDock)]
        return nodes_indices

    def export_delivery_request_nodes_indices(self, graph: OperationalGraph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DeliveryRequest)]
        return nodes_indices

    @staticmethod
    def get_delivery_request(graph: OperationalGraph, index: int) -> DeliveryRequest:
        node = list(graph.nodes)[index].internal_node
        if not isinstance(node, DeliveryRequest):
            raise TypeError(f"The given index {index} is not of a delivery request node.")
        return node

    @staticmethod
    def get_drone_loading_dock(graph: OperationalGraph, index: int) -> DroneLoadingDock:
        node = list(graph.nodes)[index].internal_node
        if not isinstance(node, DroneLoadingDock):
            raise TypeError(f"The given index {index} is not of a drone loading dock node.")
        return node

    @lru_cache()
    def export_package_type_demands(self, graph: OperationalGraph, package_type: PackageType) -> List[int]:
        delivery_request_indices = self.export_delivery_request_nodes_indices(graph)
        delivery_requests_nodes = np.array(graph.nodes)
        delivery_requests_nodes = list(delivery_requests_nodes[delivery_request_indices])
        delivery_requests = [node.internal_node for node in delivery_requests_nodes]
        base_empty_demands = [0] * len(self.export_basis_nodes_indices(graph))
        demands = base_empty_demands + [delivery_request.delivery_options[0].get_package_type_amount(package_type)
                                        for i, delivery_request in enumerate(delivery_requests)]
        return demands
