from abc import ABC, abstractmethod
from common.graph.operational.delivery_request_graph import *


class ExportDeliveryGraph(ABC):

    @abstractmethod
    def export_time_windows(self, delivery_request_graph: DeliveryRequestGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_priorities(self, delivery_request_graph: DeliveryRequestGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_travel_times(self, delivery_request_graph: DeliveryRequestGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_basis_nodes_indices(self, delivery_request_graph: DeliveryRequestGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_delivery_request_nodes_indices(self, delivery_request_graph: DeliveryRequestGraph):
        raise NotImplementedError()


