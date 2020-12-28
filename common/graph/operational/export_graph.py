from abc import ABC, abstractmethod

from common.entities.base_entities.temporal import DateTimeExtension
from common.graph.operational.operational_graph import *


class GraphExporter(ABC):

    @abstractmethod
    def export_time_windows(self, graph: OperationalGraph, zero_time: DateTimeExtension):
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


