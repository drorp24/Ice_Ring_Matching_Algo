from common.entities.delivery_request import DeliveryRequest
from common.graph.base_graph.graph_wrapper import *


class DeliveryRequestNode(GraphNode):

    def __init__(self, delivery_request: DeliveryRequest):
        super().__init__(node=delivery_request)


class DeliveryPath(DirectedEdge):

    def __init__(self, start_request: DeliveryRequest, end_request: DeliveryRequest):
        super().__init__(start_node=DeliveryRequestNode(start_request), end_node=DeliveryRequestNode(end_request))


class DeliveryRequestGraph(DirectedGraph):

    def __init__(self):
        super().__init__()

    def add_delivery_requests(self, delivery_request_nodes: [DeliveryRequestNode]):
        self.add_nodes(delivery_request_nodes)

    def add_delivery_paths(self, delivery_path: [DeliveryPath]):
        self.add_edges(delivery_path)
