from networkx import DiGraph
from time_window import TimeWindow

from common.entities.delivery_request import DeliveryRequest


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
    def time_window(self):
        return self.time_window()


class DeliveryRequestEdge:

    def __init__(self, start_request: DeliveryRequest, end_request: DeliveryRequest):
        self.start_node = start_request
        self.end_node = end_request


class DeliveryRequestGraph:

    def __init__(self):
        self.internal_graph = DiGraph()

    @property
    def nodes(self):
        return self.internal_graph.nodes

    @property
    def edges(self):
        return self.internal_graph.edges

    def add_delivery_requests(self, delivery_request_nodes: [DeliveryRequestNode]):
        self.internal_graph.add_nodes_from(delivery_request_nodes)

    def add_delivery_paths(self, delivery_request_edges: [DeliveryRequestEdge]):
        self.internal_graph.add_edges_from(delivery_request_edges)

    def calc_subgraph_in_time_window(self, time_window_scope: TimeWindow):
        nodes_at_time = [node for node in self.nodes if node.time_window in time_window_scope]
        return self.internal_graph.subgraph(nodes_at_time)

    def calc_subgraph_below_priority(self, max_priority: int):
        nodes_at_time = [node for node in self.nodes if node.priority < max_priority]
        return self.internal_graph.subgraph(nodes_at_time)
