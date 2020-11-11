from typing import Tuple, List, Any
import numpy as np
from common.graph.operational.export_graph import ExportGraph, Graph
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.delivery_request import DeliveryRequest


class ExportOrtoolsGraph(ExportGraph):

    def export_time_windows(self, graph: Graph) -> List[Tuple[int, int]]:
        nodes = graph.nodes
        time_windows = [node.get_time_window_as_time_stamps()
                        for node in nodes]
        return time_windows

    def export_priorities(self, graph: Graph) -> Any:
        nodes = graph.nodes
        priorities = np.zeros((len(nodes), len(nodes)))
        for i, origin_node in enumerate(nodes):
            for j, destination_node in enumerate(nodes):
                if i != j:
                    priorities[i, j] = destination_node.priority
        return priorities

    def export_travel_times(self, graph: Graph) -> Any:
        nodes = graph.nodes
        travel_times = np.zeros((len(nodes), len(nodes)))
        for i, start_node in enumerate(nodes):
            for j, end_node in enumerate(nodes):
                if graph.has_edge(start_node, end_node):
                    travel_times[i, j] = graph.get_edge_attributes(start_node, end_node).cost
        return travel_times.tolist()

    def export_basis_nodes_indices(self, graph: Graph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DroneLoadingDock)]
        return nodes_indices

    def export_delivery_request_nodes_indices(self, graph: Graph) -> List[int]:
        nodes = graph.nodes
        nodes_indices = [i for i, node in enumerate(nodes) if isinstance(node.internal_node, DeliveryRequest)]
        return nodes_indices
