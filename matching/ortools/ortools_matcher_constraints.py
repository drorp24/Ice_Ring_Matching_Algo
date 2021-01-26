from enum import Enum
from typing import Tuple, List

import numpy as np
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel, RoutingDimension

from common.entities.base_entities.package import PackageType
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import MatcherInput

MAX_OPERATION_TIME = 365 * 24 * 60  # minutes in year


class OrToolsDimensionDescription(Enum):
    capacity = "capacity"
    time = "time"


class ORToolsMatcherConstraints:
    def __init__(self, index_manager: RoutingIndexManager, routing_model: RoutingModel,
                 matcher_input: MatcherInput):
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input
        self._travel_times_matrix = self._graph_exporter.export_travel_times(self._matcher_input.graph)
        self._time_windows = self._graph_exporter.export_time_windows(self._matcher_input.graph,
                                                                      self._matcher_input.config.zero_time)

        self._basis_nodes_indices = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)

    def add_demand(self):
        demand_dimension_name_prefix = OrToolsDimensionDescription.capacity.value + "_"
        demand_slack = 0
        for package_type in self._matcher_input.empty_board.package_types():
            callback = getattr(self, "_get_" + str.lower(package_type.name) + "_demand_callback")
            demand_callback_index = self._routing_model.RegisterPositiveUnaryTransitCallback(callback)
            self._routing_model.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                demand_slack,
                self._matcher_input.empty_board.get_package_type_amount_per_drone_delivery(package_type),
                self._matcher_input.config.constraints.capacity.count_capacity_from_zero,
                demand_dimension_name_prefix + str.lower(package_type.name))

    def _get_tiny_demand_callback(self, from_index: np.int64) -> int:
        return self._get_package_amount_by_type(from_index, PackageType.TINY)

    def _get_small_demand_callback(self, from_index: np.int64) -> int:
        return self._get_package_amount_by_type(from_index, PackageType.SMALL)

    def _get_medium_demand_callback(self, from_index: np.int64) -> int:
        return self._get_package_amount_by_type(from_index, PackageType.MEDIUM)

    def _get_large_demand_callback(self, from_index: np.int64) -> int:
        return self._get_package_amount_by_type(from_index, PackageType.LARGE)

    def _get_package_amount_by_type(self, from_index: np.int64, package_type: PackageType) -> int:
        from_node = self._index_manager.IndexToNode(from_index)
        return self._graph_exporter.export_package_type_demands(self._matcher_input.graph, package_type)[from_node]

    def add_time(self):
        transit_callback_index = self._routing_model.RegisterTransitCallback(self._get_travel_time_callback)
        self._routing_model.AddDimension(
            transit_callback_index,
            self._matcher_input.config.constraints.time.max_waiting_time,
            MAX_OPERATION_TIME,
            self._matcher_input.config.constraints.time.count_time_from_zero,
            OrToolsDimensionDescription.time.value)
        time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.time.value)
        self._add_time_window_constraints_for_each_delivery_except_depot(time_dimension, self._time_windows)
        self._add_time_window_constraints_for_each_vehicle_start_node(time_dimension, self._time_windows)
        self._instantiate_route_start_and_end_times_to_produce_feasible_times(time_dimension)
        self._set_max_route_time_for_each_vehicle(time_dimension)

    def _instantiate_route_start_and_end_times_to_produce_feasible_times(self, time_dimension: RoutingDimension):
        for i in range(len(self._matcher_input.empty_board.empty_drone_deliveries)):
            self._routing_model.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing_model.Start(i)))
            self._routing_model.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing_model.End(i)))

    def _add_time_window_constraints_for_each_vehicle_start_node(self, time_dimension: RoutingDimension,
                                                                 time_windows: List[Tuple[int, int]]):
        for i, drone_delivery in enumerate(self._matcher_input.empty_board.empty_drone_deliveries):
            start_index = self._routing_model.Start(i)
            graph_index = self._index_manager.IndexToNode(start_index)
            time_dimension.CumulVar(start_index).SetRange(time_windows[graph_index][0],
                                                          time_windows[graph_index][1])

    def _set_max_route_time_for_each_vehicle(self, time_dimension: RoutingDimension):
        for i, drone_delivery in enumerate(self._matcher_input.empty_board.empty_drone_deliveries):
            max_route_time_in_minutes = drone_delivery.max_route_time_in_minutes
            time_dimension.SetSpanUpperBoundForVehicle(max_route_time_in_minutes, i)

    def _add_time_window_constraints_for_each_delivery_except_depot(self, time_dimension: RoutingDimension,
                                                                    time_windows: List[Tuple[int, int]]):
        for graph_index, time_window in enumerate(time_windows):
            if graph_index in self._basis_nodes_indices:
                continue
            index = self._index_manager.NodeToIndex(graph_index)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    def _get_travel_time_callback(self, from_index: np.int64, to_index: np.int64) -> np.ndarray:
        from_node = self._index_manager.IndexToNode(from_index)
        to_node = self._index_manager.IndexToNode(to_index)
        return self._travel_times_matrix[from_node][to_node]

    def add_unmatched_penalty(self):
        for node in range(1, len(self._matcher_input.graph.nodes)):
            self._routing_model.AddDisjunction([self._index_manager.NodeToIndex(node)],
                                               self._matcher_input.config.unmatched_penalty)