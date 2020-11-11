from abc import ABC, abstractmethod
from common.graph.operational.delivery_request_graph import *


class ExportGraph(ABC):

    @abstractmethod
    def export_time_windows(self, graph: Graph):
        raise NotImplementedError()

    @abstractmethod
    def export_priorities(self, graph: Graph):
        raise NotImplementedError()

    @abstractmethod
    def export_travel_times(self, graph: Graph):
        raise NotImplementedError()

    @abstractmethod
    def export_basis_nodes_indices(self, graph: Graph):
        raise NotImplementedError()

    @abstractmethod
    def export_delivery_request_nodes_indices(self, graph: Graph):
        raise NotImplementedError()


