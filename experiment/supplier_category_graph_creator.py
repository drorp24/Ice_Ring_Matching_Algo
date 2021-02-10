from common.graph.operational.graph_creator import *
from experiment.supplier_category import SupplierCategory


def create_fully_connected_graph_model(supplier_category: SupplierCategory,
                                       edge_cost_factor: float = 1.0,
                                       edge_travel_time_factor: float = 1.0) -> OperationalGraph:
    operational_graph = OperationalGraph()
    operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
    operational_graph.add_delivery_requests(supplier_category.delivery_requests)
    build_time_overlapping_dependent_connected_graph(operational_graph, edge_cost_factor, edge_travel_time_factor)
    return operational_graph


def create_clustered_delivery_requests_graph_model(supplier_category: SupplierCategory,
                                                   edge_cost_factor: float = 1.0,
                                                   edge_travel_time_factor: float = 1.0,
                                                   max_clusters_per_zone: int = 1) -> OperationalGraph:
    return create_clustered_delivery_requests_graph(delivery_requests=supplier_category.delivery_requests,
                                                    drone_loading_docks=supplier_category.drone_loading_docks,
                                                    zones=supplier_category.zones,
                                                    edge_cost_factor=edge_cost_factor,
                                                    edge_travel_time_factor=edge_travel_time_factor,
                                                    max_clusters=max_clusters_per_zone)

