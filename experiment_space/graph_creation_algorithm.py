from abc import abstractmethod

from common.graph.operational.graph_creator import *
from experiment_space.supplier_category import SupplierCategory


class GraphCreationAlgorithm:

    @abstractmethod
    def create(self, supplier_category: SupplierCategory):
        pass


class FullyConnectedGraphAlgorithm(GraphCreationAlgorithm):

    def __init__(self, edge_cost_factor: float = 1.0, edge_travel_time_factor: float = 1.0):
        self._edge_cost_factor = edge_cost_factor
        self._edge_travel_time_factor = edge_travel_time_factor

    def create(self, supplier_category: SupplierCategory):
        operational_graph = OperationalGraph()
        operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
        operational_graph.add_delivery_requests(supplier_category.delivery_requests)
        build_time_overlapping_dependent_connected_graph(operational_graph,
                                                         self._edge_cost_factor,
                                                         self._edge_travel_time_factor)
        return operational_graph


class ClusteredDeliveryRequestGraphAlgorithm(GraphCreationAlgorithm):

    def __init__(self, edge_cost_factor: float = 1.0,
                 edge_travel_time_factor: float = 1.0,
                 max_clusters_per_zone: int = 1):
        self._edge_cost_factor = edge_cost_factor
        self._edge_travel_time_factor = edge_travel_time_factor
        self._max_clusters_per_zone = max_clusters_per_zone

    def create(self, supplier_category: SupplierCategory):
        return create_clustered_delivery_requests_graph(delivery_requests=supplier_category.delivery_requests,
                                                        drone_loading_docks=supplier_category.drone_loading_docks,
                                                        zones=supplier_category.zones,
                                                        edge_cost_factor=self._edge_cost_factor,
                                                        edge_travel_time_factor=self._edge_travel_time_factor,
                                                        max_clusters=self._max_clusters_per_zone)
