from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union, Tuple
from common.entities.drone_loading_dock import DroneLoadingDock
from networkx import DiGraph, Graph, subgraph

from common.entities.delivery_request import DeliveryRequest
from common.entities.temporal import TimeWindowExtension


class Node(object):

    def __init__(self, internal_node: Union[DeliveryRequest, DroneLoadingDock]):
        self._internal_node = internal_node

    @property
    def internal_node(self):
        return self._internal_node

    def time_window(self) -> TimeWindowExtension:
        return self.internal_node.time_window

    def priority(self) -> int:
        return self.internal_node.priority

    def get_time_window_as_time_stamps(self):
        return self.internal_node.time_window.get_time_stamp()

    def __eq__(self, other):
        return self.internal_node == other.internal_node




@dataclass
class EdgeAttributes:
    cost: int


class Edge:

    def __init__(self, start_node: Node, end_node: Node,
                 edge_attributes: EdgeAttributes):
        self.start_node = start_node
        self.end_node = end_node
        self.edge_attributes = edge_attributes

    @property
    def start_node(self) -> Node:
        return self.start_node

    @property
    def end_node(self) -> Node:
        return self.end_node

    @property
    def edge_attributes(self) -> EdgeAttributes:
        return self.edge_attributes

    def to_tuple(self) -> Tuple[Node, Node]:
        return self.start_node, self.end_node


class Graph:

    def __init__(self):
        self._internal_graph = DiGraph()

    def nodes(self) -> List[Node]:
        return self._internal_graph.nodes(data=False)

    def edges(self) -> List[Edge]:
        return self._internal_graph.edges.data(data=False)

    def is_empty(self):
        return self._internal_graph.nodes.__len__() == 0

    def set_internal_graph(self, networkx_graph: DiGraph):
        self._internal_graph = networkx_graph

    def add_node(self, node: Node):
        self._internal_graph.add_node(node)

    def has_edge(self, start_node: Node, end_node: Node) -> bool:
        return self._internal_graph.has_edge(start_node, end_node)

    def add_edge(self, edge: Edge):
        self._internal_graph.add_edge(edge.start_node, edge.end_node,
                                      object=edge.edge_attributes)

    def get_edge_attributes(self, start_node: Node,
                            end_node: Node) -> EdgeAttributes:
        if self.has_edge(start_node, end_node):
            return self._internal_graph[start_node][end_node]["object"]

    def add_nodes(self, nodes: [Node]):
        for node in nodes:
            self.add_node(node)
        #self._internal_graph.add_nodes_from(nodes)

    def add_edges(self, edges: [Edge]):
        edges_list = [(edge.start_node, edge.end_node,
                       {"object": edge.edge_attributes})
                      for edge in edges]
        self._internal_graph.add_edges_from(edges_list)

    def calc_subgraph_in_time_window(self, time_window_scope: TimeWindowExtension):
        nodes_at_time = [node for node in self.nodes if node.time_window in time_window_scope]
        extracted_subgraph = self.extract_subgraph_of_nodes(nodes_at_time)
        return Graph._create_from_extracted_subgraph(extracted_subgraph)

    def calc_subgraph_below_priority(self, max_priority: int) -> Graph:
        nodes_below_priority = [node for node in self.nodes if node.priority < max_priority]
        extracted_subgraph = self.extract_subgraph_of_nodes(nodes_below_priority)
        return Graph._create_from_extracted_subgraph(extracted_subgraph)

    def extract_subgraph_of_nodes(self, nodes_in_subgraph):
        return Graph(self._internal_graph.subgraph(nodes_in_subgraph).copy())

    @staticmethod
    def _create_from_extracted_subgraph(extracted_subgraph: subgraph):
        delivery_request_subgraph = Graph()
        delivery_request_subgraph.set_internal_graph(extracted_subgraph)
        return delivery_request_subgraph
