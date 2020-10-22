from typing import Dict, Tuple

import networkx as nx


class GraphNode:
    def __init__(self, node, attributes: Dict = {}):
        self._node = node
        self._node_attributes = attributes

    @property
    def internal_node(self):
        return self._node

    @property
    def attributes(self) -> Dict:
        return self._node_attributes


class DirectedEdge:
    def __init__(self, start_node: GraphNode, end_node: GraphNode, attributes: Dict = {}):
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

    def add_edges(self, edges: [DirectedEdge]):
        [self.add_edge(edge) for edge in edges]

    def add_edge(self, edge: DirectedEdge):
        self._graph_struct.add_edge(*edge.to_tuple(), attributes=edge.attributes)

    def internal_graph(self):
        return self._graph_struct
