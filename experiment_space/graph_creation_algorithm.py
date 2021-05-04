from abc import abstractmethod

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.graph.operational.graph_creator import *
from common.utils.class_controller import name_to_class
from experiment_space.supplier_category import SupplierCategory
from matching.initial_solution import Routes
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


class GraphCreationAlgorithm(JsonableBaseEntity):

    @abstractmethod
    def create(self, supplier_category: SupplierCategory):
        pass

    @classmethod
    @abstractmethod
    def dict_to_obj(cls, dict_input):
        pass


def create_graph_algorithm_by_name(graph_algorithm_name: str):
    return name_to_class(graph_algorithm_name, __name__)


class FullyConnectedGraphAlgorithm(GraphCreationAlgorithm):

    def __init__(self, edge_cost_factor: float = 1.0, edge_travel_time_factor: float = 1.0):
        self._edge_cost_factor = edge_cost_factor
        self._edge_travel_time_factor = edge_travel_time_factor

    @property
    def edge_cost_factor(self):
        return self._edge_cost_factor

    @property
    def edge_travel_time_factor(self):
        return self._edge_travel_time_factor

    def create(self, supplier_category: SupplierCategory):
        operational_graph = OperationalGraph()
        operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
        operational_graph.add_delivery_requests(supplier_category.delivery_requests)
        build_time_overlapping_dependent_connected_graph(operational_graph,
                                                         self.edge_cost_factor,
                                                         self.edge_travel_time_factor)
        return operational_graph

    @classmethod
    def dict_to_obj(cls, dict_input):
        return FullyConnectedGraphAlgorithm(
            edge_cost_factor=dict_input['edge_cost_factor'],
            edge_travel_time_factor=dict_input['edge_travel_time_factor']
        )

    def __eq__(self, other):
        return self.edge_cost_factor == other.edge_cost_factor and \
               self.edge_travel_time_factor == other.edge_travel_time_factor


class ClusteredDeliveryRequestGraphAlgorithm(GraphCreationAlgorithm):

    def __init__(self, edge_cost_factor: float = 1.0,
                 edge_travel_time_factor: float = 1.0,
                 max_clusters_per_zone: int = 1):
        self._edge_cost_factor = edge_cost_factor
        self._edge_travel_time_factor = edge_travel_time_factor
        self._max_clusters_per_zone = max_clusters_per_zone

    @property
    def edge_cost_factor(self):
        return self._edge_cost_factor

    @property
    def edge_travel_time_factor(self):
        return self._edge_travel_time_factor

    @property
    def max_clusters_per_zone(self):
        return self._max_clusters_per_zone

    @classmethod
    def dict_to_obj(cls, dict_input):
        return ClusteredDeliveryRequestGraphAlgorithm(
            edge_cost_factor=dict_input['edge_cost_factor'],
            edge_travel_time_factor=dict_input['edge_travel_time_factor'],
            max_clusters_per_zone=dict_input['max_clusters_per_zone']
        )

    def create(self, supplier_category: SupplierCategory):
        return create_clustered_delivery_requests_graph(delivery_requests=supplier_category.delivery_requests,
                                                        drone_loading_docks=supplier_category.drone_loading_docks,
                                                        zones=supplier_category.zones,
                                                        edge_cost_factor=self._edge_cost_factor,
                                                        edge_travel_time_factor=self._edge_travel_time_factor,
                                                        max_clusters=self._max_clusters_per_zone)

    def __eq__(self, other):
        return self.edge_cost_factor == other.edge_cost_factor and \
               self.edge_travel_time_factor == other.edge_travel_time_factor and \
               self.max_clusters_per_zone == other.max_clusters_per_zone


class PackageTimeZonesDependentGraphAlgorithm(GraphCreationAlgorithm):

    def __init__(self, edge_cost_factor: float = 1.0, edge_travel_time_factor: float = 1.0):
        self._edge_cost_factor = edge_cost_factor
        self._edge_travel_time_factor = edge_travel_time_factor

    @property
    def edge_cost_factor(self):
        return self._edge_cost_factor

    @property
    def edge_travel_time_factor(self):
        return self._edge_travel_time_factor

    def create(self, supplier_category: SupplierCategory):

        operational_graph = create_package_time_zones_dependent_graph_model(
            delivery_requests=supplier_category.delivery_requests,
            drone_loading_docks=supplier_category.drone_loading_docks,
            zones=supplier_category.zones,
            edge_cost_factor=self.edge_cost_factor,
            edge_travel_time_factor=self.edge_travel_time_factor)

        return operational_graph

    @classmethod
    def dict_to_obj(cls, dict_input):
        return PackageTimeZonesDependentGraphAlgorithm(
            edge_cost_factor=dict_input['edge_cost_factor'],
            edge_travel_time_factor=dict_input['edge_travel_time_factor']
        )

    def __eq__(self, other):
        return self.edge_cost_factor == other.edge_cost_factor and \
               self.edge_travel_time_factor == other.edge_travel_time_factor


def calc_assignment_from_init_solution(matcher_input: MatcherInput,
                                       initial_routes: Routes) -> DroneDeliveryBoard:
    matcher = create_matcher(matcher_input)
    return matcher.match_from_init_solution(initial_routes)
