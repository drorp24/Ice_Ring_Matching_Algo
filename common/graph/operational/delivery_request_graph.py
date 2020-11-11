from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Union
from common.entities.drone_loading_dock import DroneLoadingDock
from networkx import DiGraph, Graph, subgraph
from time_window import TimeWindow, time_window_to_timestamps
from abc import ABC, abstractmethod
from common.entities.delivery_request import DeliveryRequest


class Node:

    def __init__(self, internal_node: Union[DeliveryRequest, DroneLoadingDock]):
        self.internal_node = internal_node

    @property
    def internal_node(self):
        return self.internal_node

    def time_window(self) -> TimeWindow:
        return self.internal_node.time_window

    def priority(self) -> int:
        return self.internal_node.priority

    def get_time_window_as_time_stamps(self):
        return g

    def __hash__(self):
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()


class DroneLoadingDockNode(Node):

    @property
    def internal_node(self) -> DroneLoadingDock:
        return self.internal_node

    def time_window(self) -> TimeWindow:
        return self.internal_node.time_window

    def priority(self) -> int:
        return 0

    def get_time_window_as_time_stamps(self):
        return time_window_to_timestamps(self.internal_node.time_window)

    def __hash__(self):
        return hash(self.internal_node)

    def __eq__(self, other):
        if isinstance(other, DroneLoadingDockNode):
            return self.internal_node == other.internal_node
        return False

    def __init__(self, drone_loading_dock: DroneLoadingDock):
        self.internal_node = drone_loading_dock


class DeliveryRequestNode:

    def __init__(self, delivery_request: DeliveryRequest):
        self.internal_node = delivery_request

    def __eq__(self, other) -> bool:
        if isinstance(other, DeliveryRequestNode):
            return self.internal_node == other.internal_node
        return False

    def __hash__(self):
        return hash(repr(self))

    @property
    def delivery_request(self) -> DeliveryRequest:
        return self.internal_node

    @property
    def priority(self):
        return self.delivery_request.priority

    @property
    def time_window(self):
        return self.delivery_request.time_window

    def get_time_window_as_time_stamps(self) -> Tuple[int, int]:
        return time_window_to_timestamps(self.delivery_request.time_window)


@dataclass
class DeliveryRequestEdgeAttributes:
    cost: int


class DeliveryRequestEdge:

    def __init__(self, start_request: DeliveryRequest, end_request: DeliveryRequest,
                 delivery_request_edge_attributes: DeliveryRequestEdgeAttributes):
        self.start_node = start_request
        self.end_node = end_request
        self.edge_attributes = delivery_request_edge_attributes

    @property
    def start_node(self) -> DeliveryRequest:
        return self.start_node

    @property
    def end_node(self) -> DeliveryRequest:
        return self.end_node

    @property
    def edge_attributes(self) -> DeliveryRequestEdgeAttributes:
        return self.edge_attributes

    @end_node.setter
    def end_node(self, value):
        self._end_node = value

    @start_node.setter
    def start_node(self, value):
        self._start_node = value

    @edge_attributes.setter
    def edge_attributes(self, value):
        self._edge_attributes = value


class DeliveryRequestGraph:

    def __init__(self):
        self.internal_graph = DiGraph()

    @property
    def nodes(self) -> List[DeliveryRequestNode]:
        return self.internal_graph.nodes(data=False)

    @property
    def edges(self) -> List[DeliveryRequestEdge]:
        internal_edges = self.internal_graph.edges.data()
        edges = [DeliveryRequestEdge(internal_edge[0], internal_edge[1], internal_edge[2]["object"])
                 for internal_edge in internal_edges]
        return edges

    def is_empty(self):
        return self.internal_graph.nodes.__len__() == 0

    def set_internal_graph(self, networkx_graph: DiGraph):
        self.internal_graph = networkx_graph

    def add_node(self, delivery_request_node: DeliveryRequestNode):
        self.internal_graph.add_node(delivery_request_node)

    def has_edge(self, start_node: DeliveryRequestNode, end_node: DeliveryRequestNode) -> bool:
        return self.internal_graph.has_edge(start_node, end_node)

    def add_edge(self, delivery_request_edge: DeliveryRequestEdge):
        self.internal_graph.add_edge(delivery_request_edge.start_node, delivery_request_edge.end_node,
                                     object=delivery_request_edge.edge_attributes)

    def get_edge_attributes(self, start_node: DeliveryRequestNode,
                            end_node: DeliveryRequestNode) -> DeliveryRequestEdgeAttributes:
        if self.has_edge(start_node, end_node):
            return self.internal_graph[start_node][end_node]["object"]

    def add_delivery_request_nodes(self, delivery_request_nodes: [DeliveryRequestNode]):
        self.internal_graph.add_nodes_from(delivery_request_nodes)

    def add_delivery_request_edges(self, delivery_request_edges: [DeliveryRequestEdge]):
        delivery_request_edges_list = [(delivery_request_edge.start_node, delivery_request_edge.end_node,
                                        {"object": delivery_request_edge.edge_attributes})
                                       for delivery_request_edge in delivery_request_edges]
        self.internal_graph.add_edges_from(delivery_request_edges_list)

    def calc_subgraph_in_time_window(self, time_window_scope: TimeWindow):
        nodes_at_time = [node for node in self.nodes if node.time_window in time_window_scope]
        extracted_subgraph = self.extract_subgraph_of_nodes(nodes_at_time)
        return DeliveryRequestGraph._create_from_extracted_subgraph(extracted_subgraph)

    def calc_subgraph_below_priority(self, max_priority: int) -> DeliveryRequestGraph:
        nodes_below_priority = [node for node in self.nodes if node.priority < max_priority]
        extracted_subgraph = self.extract_subgraph_of_nodes(nodes_below_priority)
        return DeliveryRequestGraph._create_from_extracted_subgraph(extracted_subgraph)

    def extract_subgraph_of_nodes(self, nodes_in_subgraph):
        return Graph(self.internal_graph.subgraph(nodes_in_subgraph).copy())

    @staticmethod
    def _create_from_extracted_subgraph(extracted_subgraph: subgraph):
        delivery_request_subgraph = DeliveryRequestGraph()
        delivery_request_subgraph.set_internal_graph(extracted_subgraph)
        return delivery_request_subgraph
