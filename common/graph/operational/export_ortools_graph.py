from pprint import pprint
from typing import Tuple, List
import numpy as np

from common.entities.package import PackageType
from common.entities.temporal import DateTimeExtension
from common.graph.operational.export_graph import GraphExporter, OperationalGraph
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.delivery_request import DeliveryRequest


class OrtoolsGraphExporter(GraphExporter):

    def export_time_windows(self, graph: OperationalGraph, zero_time: DateTimeExtension) -> List[Tuple[int, int]]:
        nodes = graph.nodes
        time_windows = [tuple(map(int, node.time_window.get_relative_time_in_min(zero_time)))
                        for node in nodes]
        return time_windows

    def export_priorities(self, graph: OperationalGraph) -> List[int]:
        nodes = list(graph.nodes)
        priorities = [node.priority for node in nodes]
        return priorities

    def export_travel_times(self, graph: OperationalGraph) -> List[List[int]]:
        nodes = list(graph.nodes)
        edges = list(graph.edges)
        travel_times = np.inf *np.ones((len(nodes), len(nodes)))
        for i in range(len(nodes)):
            travel_times[i,i] = 0
        for edge in edges:
            origin_idx = nodes.index(edge.start_node)
            destination_idx = nodes.index(edge.end_node)
            travel_times[origin_idx, destination_idx] = edge.attributes.cost
            travel_times[destination_idx, origin_idx] = edge.attributes.cost
        return travel_times.tolist()

    def export_basis_nodes_indices(self, graph: OperationalGraph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DroneLoadingDock)]
        return nodes_indices

    def export_delivery_request_nodes_indices(self, graph: OperationalGraph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DeliveryRequest)]
        return nodes_indices

    def get_delivery_request(self, graph: OperationalGraph, index: int) -> DeliveryRequest:
        node = list(graph.nodes)[index].internal_node
        if not isinstance(node, DeliveryRequest):
            raise TypeError(f"The given index {index} is not of a delivery request node.")
        return node

    def export_package_type_demands(self, graph: OperationalGraph, package_type: PackageType) -> List[int]:
        delivery_request_indices = self.export_delivery_request_nodes_indices(graph)
        delivery_requests_nodes = np.array(graph.nodes)
        delivery_requests_nodes = list(delivery_requests_nodes[delivery_request_indices])
        delivery_requests = [node.internal_node for node in delivery_requests_nodes]
        base_empty_demands = [0 for base_node in self.export_basis_nodes_indices(graph)]
        demands = base_empty_demands + [delivery_request.delivery_options[0].get_amount_of_package_type(package_type)
                                     for i, delivery_request in enumerate(delivery_requests)]
        return demands
