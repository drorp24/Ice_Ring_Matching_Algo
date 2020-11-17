from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

from networkx import DiGraph, Graph, subgraph

from common.entities.delivery_request import DeliveryRequest
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.temporal import TimeWindowExtension


class OperationalNode:

    def __init__(self, internal_node: Union[DeliveryRequest, DroneLoadingDock]):
        self._internal = internal_node

    @property
    def internal_node(self) -> Union[DeliveryRequest, DroneLoadingDock]:
        return self._internal

    @property
    def internal_type(self):
        return type(self.internal_node)

    @property
    def priority(self) -> int:
        return self.internal_node.priority

    @property
    def time_window(self) -> TimeWindowExtension:
        return self.internal_node.time_window

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.internal_node == other.internal_node

    def __hash__(self):
        return hash(self._internal)


@dataclass
class OperationalEdgeAttribs:

    def __init__(self, cost: int):
        self.cost = cost


class OperationalEdge(object):

    def __init__(self, start_node: OperationalNode, end_node: OperationalNode, attributes: OperationalEdgeAttribs):
        self.start_node = start_node
        self.end_node = end_node
        self.attributes = attributes

    def to_tuple(self):
        return self.start_node, self.end_node, self.attributes.__dict__

    def __hash__(self):
        return self.to_tuple().__hash__()


class OperationalGraph:

    def __init__(self):
        self._internal_graph = DiGraph()

    @property
    def nodes(self) -> List[OperationalNode]:
        return self._internal_graph.nodes(data=False)

    @property
    def edges(self) -> List[OperationalEdge]:
        internal_edges = self._internal_graph.edges.data(data=True)
        return [OperationalEdge(edge[0], edge[1], OperationalEdgeAttribs(edge[2]["cost"])) for edge in
                internal_edges]

    def is_empty(self):
        return self._internal_graph.nodes.__len__() == 0

    def set_internal_graph(self, networkx_graph: DiGraph):
        self._internal_graph = networkx_graph

    def add_drone_loading_docks(self, drone_loading_docks: [DroneLoadingDock]):
        self.add_operational_nodes([OperationalNode(dl) for dl in drone_loading_docks])

    def add_delivery_requests(self, delivery_requests: [DeliveryRequest]):
        self.add_operational_nodes([OperationalNode(dr) for dr in delivery_requests])

    def add_operational_nodes(self, operational_nodes: [OperationalNode]):
        self._internal_graph.add_nodes_from(operational_nodes)

    def add_operational_edges(self, operational_edges: [OperationalEdge]):
        self._internal_graph.add_edges_from([dr.to_tuple() for dr in operational_edges])

    def calc_subgraph_in_time_window(self, time_window_scope: TimeWindowExtension):
        nodes_at_time = [node for node in self.nodes if node.time_window in time_window_scope]
        extracted_subgraph = self.extract_subgraph_of_nodes(nodes_at_time)
        return OperationalGraph._create_from_extracted_subgraph(extracted_subgraph)

    def calc_subgraph_below_priority(self, max_priority: int) -> OperationalGraph:
        nodes_below_priority = [node for node in self.nodes if node.priority < max_priority]
        extracted_subgraph = self.extract_subgraph_of_nodes(nodes_below_priority)
        return OperationalGraph._create_from_extracted_subgraph(extracted_subgraph)

    def extract_subgraph_of_nodes(self, nodes_in_subgraph):
        return Graph(self._internal_graph.subgraph(nodes_in_subgraph).copy())

    @staticmethod
    def _create_from_extracted_subgraph(extracted_subgraph: subgraph):
        delivery_request_subgraph = OperationalGraph()
        delivery_request_subgraph.set_internal_graph(extracted_subgraph)
        return delivery_request_subgraph
