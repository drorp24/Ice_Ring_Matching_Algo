import sys
from enum import Enum
from typing import Tuple, List

import numpy as np
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel, RoutingDimension

from common.entities.base_entities.package import PackageType
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import MatcherInput

MAX_OPERATION_TIME = 365 * 24 * 60  # minutes in year
MAX_DEMAND_RELOAD = 1000
MAX_SESSION_TIME = 60


class OrToolsDimensionDescription(Enum):
    capacity = "capacity"
    travel_cost = "travel_cost"
    travel_time = "travel_time"
    session_time = "session_time"


class ORToolsMatcherConstraints:
    def __init__(self, index_manager: RoutingIndexManager, routing_model: RoutingModel,
                 matcher_input: MatcherInput, reloading_depos_arrive_indices: [int],
                 reloading_depos_depart_indices: [int]):
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input
        self._travel_cost_matrix = self._graph_exporter.export_travel_costs(self._matcher_input.graph)
        self._travel_time_matrix = self._graph_exporter.export_travel_times(self._matcher_input.graph)
        self._time_windows = self._graph_exporter.export_time_windows(self._matcher_input.graph,
                                                                      self._matcher_input.config.zero_time)
        self._basis_nodes_indices = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)
        self._arrive_indices = reloading_depos_arrive_indices
        self._depart_indices = reloading_depos_depart_indices
        self._reloading_virtual_depos_indices = self._arrive_indices + self._depart_indices
        self._depos = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph) \
            + self._reloading_virtual_depos_indices
        self._num_of_nodes = len(self._matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)

    def add_travel_cost(self):
        travel_cost_callback_index = self._routing_model.RegisterTransitCallback(self.create_travel_cost_evaluator())
        self._routing_model.AddDimension(
            travel_cost_callback_index,
            self._matcher_input.config.constraints.time.max_waiting_time,
            MAX_OPERATION_TIME,
            self._matcher_input.config.constraints.time.count_time_from_zero,
            OrToolsDimensionDescription.travel_cost.value)

    def add_travel_time(self):
        travel_time_callback_index = self._routing_model.RegisterTransitCallback(self.create_travel_time_evaluator())
        self._routing_model.AddDimension(
            travel_time_callback_index,
            MAX_OPERATION_TIME,
            MAX_OPERATION_TIME,
            self._matcher_input.config.constraints.time.count_time_from_zero,
            OrToolsDimensionDescription.travel_time.value)
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        self._add_time_window_constraints_for_each_delivery_except_depot(travel_time_dimension, self._time_windows)
        self._add_time_window_constraints_for_each_vehicle_start_node(travel_time_dimension, self._time_windows)
        for node in range(self._num_of_nodes):
            index = self._index_manager.NodeToIndex(node)
            if node in self._depart_indices:
                travel_time_dimension.SlackVar(index).SetMin(120)
            else:
                travel_time_dimension.SlackVar(index).SetMax(0)
            self._routing_model.AddToAssignment(travel_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(travel_time_dimension.SlackVar(index))
        for node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
            index = self._index_manager.NodeToIndex(node)
            coefficient = max(self._graph_exporter.export_priorities(self._matcher_input.graph)) / self._graph_exporter.export_priorities(self._matcher_input.graph)[node]
            travel_time_dimension.SetCumulVarSoftUpperBound(index, 0, int(coefficient))
        for vehicle_id in range(self._matcher_input.empty_board.amount_of_formations()):
            index = self._routing_model.Start(vehicle_id)
            self._routing_model.AddToAssignment(travel_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(travel_time_dimension.SlackVar(index))

    def add_session_time(self):
        session_time_callback_index = self._routing_model.RegisterTransitCallback(self.create_session_evaluator())
        self._routing_model.AddDimension(
            session_time_callback_index,
            MAX_SESSION_TIME,
            MAX_SESSION_TIME,
            True,
            OrToolsDimensionDescription.session_time.value)

        session_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.session_time.value)
        for node_index in range(self._num_of_nodes):
            index = self._index_manager.NodeToIndex(node_index)
            if node_index not in self._depos:
                session_time_dimension.SlackVar(index).SetValue(0)
            self._routing_model.AddToAssignment(session_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(session_time_dimension.SlackVar(index))
        for vehicle_id in range(self._matcher_input.empty_board.amount_of_formations()):
            index = self._routing_model.Start(vehicle_id)
            self._routing_model.AddToAssignment(session_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(session_time_dimension.SlackVar(index))

    def add_demand(self):
        demand_dimension_name_prefix = OrToolsDimensionDescription.capacity.value + "_"
        for package_type in self._matcher_input.empty_board.package_types():
            demand_dimension_name = demand_dimension_name_prefix + str.lower(package_type.name)
            callback = getattr(self, "_get_" + str.lower(package_type.name) + "_demand_callback")
            demand_callback_index = self._routing_model.RegisterPositiveUnaryTransitCallback(callback)
            self._routing_model.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                max(self._matcher_input.empty_board.get_package_type_amount_per_drone_delivery(package_type)),
                self._matcher_input.empty_board.get_package_type_amount_per_drone_delivery(package_type),
                self._matcher_input.config.constraints.capacity.count_capacity_from_zero,
                demand_dimension_name)
            demand_dimension = self._routing_model.GetDimensionOrDie(demand_dimension_name)
            for node_index in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
                index = self._index_manager.NodeToIndex(node_index)
                demand_dimension.SlackVar(index).SetValue(0)
            for node_index in self._arrive_indices:
                index = self._index_manager.NodeToIndex(node_index)
                demand_dimension.SetCumulVarSoftUpperBound(index, 0, 1000)

    def add_unmatched_penalty(self):
        for node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
            self._routing_model.AddDisjunction([self._index_manager.NodeToIndex(node)],
                                               self._matcher_input.config.unmatched_penalty)
        for node in self._reloading_virtual_depos_indices:
            self._routing_model.AddDisjunction([self._index_manager.NodeToIndex(node)],
                                               0)

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
        package_amount_by_type = 0
        if from_node in self._basis_nodes_indices or from_node in self._depart_indices:
            package_amount_by_type = max(self._matcher_input.empty_board.get_package_type_amount_per_drone_delivery(package_type))
        elif from_node in self._arrive_indices:
            package_amount_by_type = 0
        else:
            package_amount_by_type = -1 * self._graph_exporter.export_package_type_demands(self._matcher_input.graph, package_type)[from_node]
        return package_amount_by_type

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

    def _add_time_window_constraints_for_each_delivery_except_depot(self, time_dimension: RoutingDimension,
                                                                    time_windows: List[Tuple[int, int]]):
        for graph_index, time_window in enumerate(time_windows):
            if graph_index in self._basis_nodes_indices:
                continue
            index = self._index_manager.NodeToIndex(graph_index)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        for node in self._reloading_virtual_depos_indices:
            index = self._index_manager.NodeToIndex(node)
            time_dimension.CumulVar(index).SetRange(self._time_windows[0][0], self._time_windows[0][1])

    def create_travel_cost_evaluator(self):

        def travel_cost(from_node, to_node):
            if from_node == to_node:
                return 0
            if from_node in self._arrive_indices and to_node == (from_node + 1):
                return 0
            if from_node in self._arrive_indices and to_node != (from_node + 1):
                return sys.maxsize
            if to_node in self._depart_indices and from_node != (to_node - 1):
                return sys.maxsize
            if self._are_nodes_consecutive_depos(from_node, to_node):
                return sys.maxsize
            if from_node in self._reloading_virtual_depos_indices:
                from_node = 0
            elif to_node in self._reloading_virtual_depos_indices:
                to_node = 0
            travel_cost = self._travel_cost_matrix[from_node][to_node]
            return travel_cost

        _travel_cost = {}
        for from_node in range(self._num_of_nodes):
            _travel_cost[from_node] = {}
            for to_node in range(self._num_of_nodes):
                if from_node == to_node:
                    _travel_cost[from_node][to_node] = 0
                else:
                    _travel_cost[from_node][to_node] = int(
                        travel_cost(
                            from_node, to_node))

        def travel_cost_evaluator(from_node, to_node):
            return _travel_cost[self._index_manager.IndexToNode(from_node)][self._index_manager.IndexToNode(
                to_node)]

        return travel_cost_evaluator

    def create_travel_time_evaluator(self):

        def travel_time(from_node, to_node):
            if from_node == to_node:
                return 0
            if from_node in self._arrive_indices and to_node == (from_node + 1):
                return 0
            if from_node in self._arrive_indices and to_node != (from_node + 1):
                return sys.maxsize
            if to_node in self._depart_indices and from_node != (to_node - 1):
                return sys.maxsize
            if self._are_nodes_consecutive_depos(from_node, to_node):
                return sys.maxsize
            if from_node in self._reloading_virtual_depos_indices:
                from_node = 0
            elif to_node in self._reloading_virtual_depos_indices:
                to_node = 0
            travel_time = self._travel_time_matrix[from_node][to_node]
            return travel_time

        _travel_time = {}
        for from_node in range(self._num_of_nodes):
            _travel_time[from_node] = {}
            for to_node in range(self._num_of_nodes):
                if from_node == to_node:
                    _travel_time[from_node][to_node] = 0
                else:
                    _travel_time[from_node][to_node] = int(
                        travel_time(
                            from_node, to_node))

        def time_evaluator(from_node, to_node):
            return _travel_time[self._index_manager.IndexToNode(from_node)][self._index_manager.IndexToNode(
                to_node)]

        return time_evaluator

    def create_session_evaluator(self):

        def session_time(from_node, to_node):
            if from_node == to_node:
                return 0
            if from_node in self._arrive_indices and to_node == (from_node + 1):
                return -MAX_SESSION_TIME
            if from_node in self._arrive_indices and to_node != (from_node + 1):
                return sys.maxsize
            if to_node in self._depart_indices and from_node != (to_node - 1):
                return sys.maxsize
            if self._are_nodes_consecutive_depos(from_node, to_node):
                return sys.maxsize
            if from_node in self._reloading_virtual_depos_indices:
                from_node = 0
            elif to_node in self._reloading_virtual_depos_indices:
                to_node = 0
            session_time = self._travel_time_matrix[from_node][to_node]
            return session_time

        _session_time = {}
        for from_node in range(self._num_of_nodes):
            _session_time[from_node] = {}
            for to_node in range(self._num_of_nodes):
                if from_node == to_node:
                    _session_time[from_node][to_node] = 0
                else:
                    _session_time[from_node][to_node] = int(
                        session_time(
                            from_node, to_node))

        def session_evaluator(from_node, to_node):
            return _session_time[self._index_manager.IndexToNode(from_node)][self._index_manager.IndexToNode(
                to_node)]

        return session_evaluator

    def _are_nodes_consecutive_depos(self, from_node, to_node) -> bool:
        return from_node in self._depos and to_node in self._depos
