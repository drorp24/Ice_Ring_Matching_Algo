from abc import ABC, abstractmethod
from common.graph.operational.delivery_request_graph import *


class GraphExporter(ABC):

    @abstractmethod
    def export_time_windows(self, graph: OperationalGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_priorities(self, graph: OperationalGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_travel_times(self, graph: OperationalGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_basis_nodes_indices(self, graph: OperationalGraph):
        raise NotImplementedError()

    @abstractmethod
    def export_delivery_request_nodes_indices(self, graph: OperationalGraph):
        raise NotImplementedError()


