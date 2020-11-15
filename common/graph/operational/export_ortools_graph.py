from typing import Tuple, List, Any
import numpy as np

from common.entities.package import PackageType
from common.graph.operational.export_graph import ExportGraph, OperationalGraph
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.delivery_request import DeliveryRequest


class OrtoolsGraphExporter(ExportGraph):

    def export_time_windows(self, graph: OperationalGraph) -> List[Tuple[int, int]]:
        nodes = graph.nodes
        time_windows = [node.time_window.get_time_stamp()
                        for node in nodes]
        return time_windows

    def export_priorities(self, graph: OperationalGraph) -> Any:
        nodes = list(graph.nodes)
        priorities = [node.priority for node in nodes]
        return priorities

    def export_travel_times(self, graph: OperationalGraph) -> Any:
        nodes = list(graph.nodes)
        edges = list(graph.edges)
        travel_times = np.zeros((len(nodes), len(nodes)))
        for edge in edges:
            origin_idx = nodes.index(edge[0])
            destination_idx = nodes.index(edge[1])
            travel_times[origin_idx, destination_idx] = edge[2]["cost"]
        return travel_times

    def export_basis_nodes_indices(self, graph: OperationalGraph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DroneLoadingDock)]
        return nodes_indices

    def export_delivery_request_nodes_indices(self, graph: OperationalGraph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DeliveryRequest)]
        return nodes_indices

    def export_package_type_demands(self, graph: OperationalGraph, package_type: PackageType) -> List[int]:
        delivery_request_indices = self.export_delivery_request_nodes_indices(graph)
        delivery_requests_nodes = np.array(graph.nodes)
        delivery_requests_nodes = list(delivery_requests_nodes[delivery_request_indices])
        delivery_requests = [node.internal_node for node in delivery_requests_nodes]
        return [delivery_request.delivery_options[0].get_package_type_demand(package_type)
                for i, delivery_request in enumerate(delivery_requests)]

