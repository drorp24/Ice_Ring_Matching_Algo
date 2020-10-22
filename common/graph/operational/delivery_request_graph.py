from typing import Dict

from common.entities.delivery_request import DeliveryRequest
from common.graph.base_graph.graph_wrapper import *


class DeliveryRequestNode(GraphNode):

    def __init__(self, delivery_request: DeliveryRequest):
        super.__init__(node=delivery_request)


class DeliveryPath(DirectedEdge):

    def __init__(self, start_request: DeliveryRequest, end_request: DeliveryRequest):
        super.__init__(start_node=start_request, end_node=end_request)


class DeliveryRequestGraph(DirectedGraph):

    def __init__(self):
        super.__init__()

    def add_delivery_requests(self, delivery_requests: [DeliveryRequest]):
        self.add_nodes(delivery_requests)

    def add_path(self, delivery_path: DeliveryPath):
        self.add_edge(delivery_path)
