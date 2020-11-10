from __future__ import annotations
from typing import List

from networkx import DiGraph, Graph, subgraph
from time_window import TimeWindow

from common.entities.delivery_request import DeliveryRequest
from common.entities.temporal import TimeWindowExtension


class DeliveryRequestNode:

    def __init__(self, delivery_request: DeliveryRequest):
        self.internal_node = delivery_request

    @property
    def delivery_request(self) -> DeliveryRequest:
        return self.internal_node

    @property
    def priority(self):
        return self.delivery_request.priority

    @property
    def time_window(self) -> TimeWindowExtension:
        return self.delivery_request.time_window


class DeliveryRequestEdge:

    def __init__(self, start_request: DeliveryRequestNode, end_request: DeliveryRequestNode):
        self.start_node = start_request
        self.end_node = end_request

    def to_tuple(self):
        return self.start_node, self.end_node


class DeliveryRequestGraph:

    def __init__(self):
        self.internal_graph = DiGraph()

    @property
    def nodes(self) -> List[DeliveryRequestNode]:
        return self.internal_graph.nodes(data=False)

    @property
    def edges(self) -> List[DeliveryRequestEdge]:
        return self.internal_graph.edges.data(data=False)

    def is_empty(self):
        return self.internal_graph.nodes.__len__() == 0

    def set_internal_graph(self, networkx_graph: DiGraph):
        self.internal_graph = networkx_graph

    def add_delivery_requests(self, delivery_requests: [DeliveryRequest]):
        self.add_delivery_request_nodes([DeliveryRequestNode(dr) for dr in delivery_requests])

    def add_delivery_request_nodes(self, delivery_request_nodes: [DeliveryRequestNode]):
        self.internal_graph.add_nodes_from(delivery_request_nodes)

    def add_delivery_request_edges(self, delivery_request_edges: [DeliveryRequestEdge]):
        self.internal_graph.add_edges_from([dr.to_tuple() for dr in delivery_request_edges])

    def calc_subgraph_in_time_window(self, time_window_scope: TimeWindowExtension):
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
