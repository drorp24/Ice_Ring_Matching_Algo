from typing import Dict, Tuple

import networkx as nx


class GraphNode:
    def __init__(self, node: object, attributes=None):
        if attributes is None:
            attributes = {}
        self._node = node
        self._node_attributes = attributes

    @property
    def internal_node(self):
        return self._node

    @property
    def attributes(self) -> Dict:
        return self._node_attributes


class DirectedEdge:
    def __init__(self, start_node: GraphNode, end_node: GraphNode, attributes=None):
        if attributes is None:
            attributes = {}
        self._start_node = start_node
        self._end_node = end_node
        self._edge_attributes = attributes

    def to_tuple(self) -> Tuple:
        return self._start_node, self._end_node

    @property
    def start_node(self):
        return self._start_node

    @property
    def end_node(self):
        return self._end_node

    @property
    def attributes(self) -> Dict:
        return self._edge_attributes


class DirectedGraph:

    def __init__(self):
        self._graph_struct = nx.DiGraph()

    def add_nodes(self, nodes: [GraphNode]):
        [self.add_node(node) for node in nodes]

    def add_node(self, node: GraphNode):
        self._graph_struct.add_node(node, attributes=node.attributes)

    def remove_node(self, node: GraphNode):
        self._graph_struct.remove_node(node)

    def remove_nodes(self, nodes: [GraphNode]):
        [self.remove_node(node) for node in nodes]

    def add_edges(self, edges: [DirectedEdge]):
        [self.add_edge(edge) for edge in edges]

    def add_edge(self, edge: DirectedEdge):
        self._graph_struct.add_edge(*edge.to_tuple(), attributes=edge.attributes)

    def remove_edge(self, edge: DirectedEdge):
        self._graph_struct.remove_edge(edge.start_node, edge.end_node)

    def remove_edges(self, edges: [DirectedEdge]):
        [self.remove_edge(edge) for edge in edges]

    def _internal_graph(self):
        return self._graph_struct

    def __contains__(self, item: [GraphNode, DirectedEdge]) -> bool:
        if isinstance(item, GraphNode):
            return self._graph_struct.has_node(item)
        if isinstance(item, DirectedEdge):
            return self._graph_struct.has_edge(item)
        return False

    @property
    def num_of_edges(self):
        return self._graph_struct.number_of_edges()

    @property
    def num_of_nodes(self):
        return self._graph_struct.number_of_nodes()
