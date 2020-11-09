from typing import Tuple, List, Any
import numpy as np
from common.graph.operational.export_graph import ExportDeliveryGraph, DeliveryRequestGraph


class ExportOrtoolsGraph(ExportDeliveryGraph):

    def export_time_windows(self, delivery_request_graph: DeliveryRequestGraph) -> List[Tuple[int, int]]:
        delivery_request_nodes = delivery_request_graph.nodes
        time_windows = [delivery_request_node.get_time_window_as_time_stamps()
                        for delivery_request_node in delivery_request_nodes]
        return time_windows

    def export_priorities(self, delivery_request_graph: DeliveryRequestGraph) -> Any:
        delivery_request_nodes = delivery_request_graph.nodes
        priorities = np.zeros((len(delivery_request_nodes), len(delivery_request_nodes)))
        for i, origin_delivery_request_node in enumerate(delivery_request_nodes):
            for j, destination_delivery_request_node in enumerate(delivery_request_nodes):
                if i != j:
                    priorities[i, j] = destination_delivery_request_node.priority
        return priorities

    def export_travel_times(self, delivery_request_graph: DeliveryRequestGraph) -> Any:
        nodes = delivery_request_graph.nodes
        travel_times = np.zeros((len(nodes), len(nodes)))
        for i, start_node in enumerate(nodes):
            for j, end_node in enumerate(nodes):
                if delivery_request_graph.has_edge(start_node, end_node):
                    travel_times[i, j] = delivery_request_graph.get_edge_attributes(start_node, end_node).cost
        return travel_times.tolist()

    def export_basis_nodes_indices(self, delivery_request_graph: DeliveryRequestGraph) -> List[int]:
        return [0]

    def export_delivery_request_nodes_indices(self, delivery_request_graph: DeliveryRequestGraph) -> List[int]:
        nodes = delivery_request_graph.nodes
        nodes_indices = [i + 1 for i, node in enumerate(nodes)]
        return nodes_indices
