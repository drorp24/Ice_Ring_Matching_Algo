import sys
from enum import Enum
from functools import lru_cache
from typing import Tuple, List

import numpy as np
from ortools.constraint_solver.pywrapcp import RoutingModel, RoutingDimension

from common.entities.base_entities.package import PackageType
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import MatcherInput
from matching.ortools.ortools_index_manager_wrapper import OrToolsIndexManagerWrapper
from matching.ortools.ortools_matcher import Reloader

MAX_OPERATION_TIME = 365 * 24 * 60  # minutes in year


class OrToolsDimensionDescription(Enum):
    capacity = "capacity"
    travel_cost = "travel_cost"
    travel_time = "travel_time"
    session_time = "session_time"
    priority = "priority"


class ORToolsMatcherConstraints:
    def __init__(self, index_manager: OrToolsIndexManagerWrapper, routing_model: RoutingModel,
                 matcher_input: MatcherInput, reloader: Reloader):
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
        self._reloading_depots_per_vehicle = reloading_depots_per_vehicle
        self._vehicle_per_reloading_depot = vehicle_per_reloading_depot

    def add_travel_cost(self):
        travel_cost_callback_index = self._routing_model.RegisterTransitCallback(self._create_travel_cost_evaluator())
        self._routing_model.AddDimension(
            travel_cost_callback_index,
            MAX_OPERATION_TIME,
            MAX_OPERATION_TIME,
            self._matcher_input.config.constraints.travel_time.count_time_from_zero,
            OrToolsDimensionDescription.travel_cost.value)

    def add_travel_time(self):
        travel_time_callback_index = self._routing_model.RegisterTransitCallback(self._create_travel_time_evaluator())
        self._routing_model.AddDimension(
            travel_time_callback_index,
            MAX_OPERATION_TIME,
            MAX_OPERATION_TIME,
            self._matcher_input.config.constraints.travel_time.count_time_from_zero,
            OrToolsDimensionDescription.travel_time.value)
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        self._add_time_window_constraints_for_each_delivery_except_depot(travel_time_dimension, self._time_windows)
        self._add_time_window_constraints_for_each_vehicle_start_node(travel_time_dimension, self._time_windows)
        self._set_max_route_time_for_each_vehicle(travel_time_dimension)
        self._set_waiting_time_for_each_node(travel_time_dimension)
        self._add_to_objective_minimize_delivery_time_of_high_priority(travel_time_dimension)
        self._add_vehicle_start_node_index_transit_and_slack_vars_to_solution(travel_time_dimension)

    def add_session_time(self):
        session_time_callback_index = self._routing_model.RegisterTransitCallback(self._create_session_evaluator())
        self._routing_model.AddDimension(
            session_time_callback_index,
            self._matcher_input.config.constraints.session_time.max_session_time,
            self._matcher_input.config.constraints.session_time.max_session_time,
            True,
            OrToolsDimensionDescription.session_time.value)

        session_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.session_time.value)
        self._allow_only_depos_to_have_waiting_time(session_time_dimension)
        self._add_vehicle_start_node_index_transit_and_slack_vars_to_solution(session_time_dimension)

    def add_demand(self):
        demand_dimension_name_prefix = OrToolsDimensionDescription.capacity.value + "_"
        for package_type in PackageType:
            demand_dimension_name = demand_dimension_name_prefix + str.lower(package_type.name)
            demand_callback_index = self._routing_model.RegisterUnaryTransitCallback(
                self._create_demand_evaluator(package_type))
            max_capacity = max(self._matcher_input.delivering_drones_board.get_package_type_amount_per_drone_delivery(package_type))
            self._routing_model.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                max_capacity,
                self._matcher_input.delivering_drones_board.get_package_type_amount_per_drone_delivery(package_type),
                self._matcher_input.config.constraints.capacity.count_capacity_from_zero,
                demand_dimension_name)
            demand_dimension = self._routing_model.GetDimensionOrDie(demand_dimension_name)
            self._add_to_objective_minimize_return_not_empty(demand_dimension, max_capacity)

    def add_unmatched_penalty(self):
        for node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
            self._routing_model.AddDisjunction([self._index_manager.node_to_index(node)],
                                               self._matcher_input.config.unmatched_penalty)
        unmatched_reloading_virtual_depo_penalty = 0
        for node in self._reloading_virtual_depos_indices[1:]:
            self._routing_model.AddDisjunction([self._index_manager.node_to_index(node)],
                                               unmatched_reloading_virtual_depo_penalty)

    def _add_vehicle_start_node_index_transit_and_slack_vars_to_solution(self, dimension):
        for vehicle_id in range(self._matcher_input.delivering_drones_board.amount_of_formations()):
            index = self._routing_model.Start(vehicle_id)
            self._routing_model.AddToAssignment(dimension.TransitVar(index))
            self._routing_model.AddToAssignment(dimension.SlackVar(index))

    def _add_to_objective_minimize_delivery_time_of_high_priority(self, travel_time_dimension):
        for node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
            index = self._index_manager.node_to_index(node)
            coefficient = max(self._graph_exporter.export_priorities(self._matcher_input.graph)) \
                / (self._graph_exporter.export_priorities(self._matcher_input.graph)[node] + 1)
            route_start_time = 0
            travel_time_dimension.SetCumulVarSoftUpperBound(index, route_start_time, int(coefficient))

    def _set_waiting_time_for_each_node(self, travel_time_dimension):
        for node in range(self._num_of_nodes):
            index = self._index_manager.node_to_index(node)
            if node in self._depart_indices:
                travel_time_dimension.SlackVar(index).SetMin(
                    self._matcher_input.config.constraints.travel_time.reloading_time)
            else:
                travel_time_dimension.SlackVar(index).SetMax(0)
            self._routing_model.AddToAssignment(travel_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(travel_time_dimension.SlackVar(index))

    def _allow_only_depos_to_have_waiting_time(self, session_time_dimension):
        for node_index in range(self._num_of_nodes):
            index = self._index_manager.node_to_index(node_index)
            if node_index not in self._depos:
                session_time_dimension.SlackVar(index).SetValue(0)
            self._routing_model.AddToAssignment(session_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(session_time_dimension.SlackVar(index))

    def _add_to_objective_minimize_return_not_empty(self, demand_dimension, max_capacity):
        for node_index in self._arrive_indices:
            index = self._index_manager.node_to_index(node_index)
            demand_dimension.SetCumulVarSoftLowerBound(index, max_capacity,
                                                       self._matcher_input.config.constraints
                                                       .capacity.capacity_cost_coefficient)
        for node_index in range(self._num_of_nodes):
            index = self._index_manager.node_to_index(node_index)
            self._routing_model.AddToAssignment(demand_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(demand_dimension.SlackVar(index))
        for vehicle_id in range(self._matcher_input.delivering_drones_board.amount_of_formations()):
            end_index = self._routing_model.End(vehicle_id)
            demand_dimension.SetCumulVarSoftLowerBound(end_index, max_capacity,
                                                       self._matcher_input.config.constraints
                                                       .capacity.capacity_cost_coefficient)
            index = self._routing_model.Start(vehicle_id)
            self._routing_model.AddToAssignment(demand_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(demand_dimension.SlackVar(index))

    def _add_time_window_constraints_for_each_vehicle_start_node(self, time_dimension: RoutingDimension,
                                                                 time_windows: List[Tuple[int, int]]):
        for i, drone_delivery in enumerate(self._matcher_input.delivering_drones_board.delivering_drones_list):
            start_index = self._routing_model.Start(i)
            graph_index = self._index_manager.index_to_node(start_index)
            time_dimension.CumulVar(start_index).SetRange(time_windows[graph_index][0],
                                                          time_windows[graph_index][1])

    def _add_time_window_constraints_for_each_delivery_except_depot(self, time_dimension: RoutingDimension,
                                                                    time_windows: List[Tuple[int, int]]):
        for graph_index, time_window in enumerate(time_windows):
            if graph_index in self._basis_nodes_indices:
                continue
            index = self._index_manager.node_to_index(graph_index)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        for node in self._reloading_virtual_depos_indices:
            index = self._index_manager.node_to_index(node)
            vehicle_of_node = self._vehicle_per_reloading_depot[node]
            dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
            original_depo = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            time_dimension.CumulVar(index).SetRange(self._time_windows[original_depo][0], self._time_windows[original_depo][1])

    def _create_travel_cost_evaluator(self):

        def travel_cost(_from_node, _to_node):
            if _from_node == _to_node:
                return 0
            if _from_node in self._arrive_indices and _to_node == (_from_node + 1):
                return 0
            if _from_node in self._arrive_indices and _to_node != (_from_node + 1):
                return sys.maxsize
            if _to_node in self._depart_indices and _from_node != (_to_node - 1):
                return sys.maxsize
            if self._are_nodes_consecutive_depos(_from_node, _to_node):
                return sys.maxsize
            if _from_node in self._reloading_virtual_depos_indices:
                vehicle_of_node = self._vehicle_per_reloading_depot[_from_node]
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
                _from_node = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            elif _to_node in self._reloading_virtual_depos_indices:
                vehicle_of_node = self._vehicle_per_reloading_depot[_to_node]
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
                _to_node = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            graph_travel_cost = self._travel_cost_matrix[_from_node][_to_node]
            return graph_travel_cost

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

        @lru_cache()
        def travel_cost_evaluator(_from_index, _to_index):
            return _travel_cost[self._index_manager.index_to_node(_from_index)][self._index_manager.index_to_node(
                _to_index)]

        return travel_cost_evaluator

    def _create_travel_time_evaluator(self):

        def travel_time(_from_node, _to_node):
            if _from_node == _to_node:
                return 0
            if _from_node in self._arrive_indices and _to_node == (_from_node + 1):
                return 0
            if _from_node in self._arrive_indices and _to_node != (_from_node + 1):
                return sys.maxsize
            if _to_node in self._depart_indices and _from_node != (_to_node - 1):
                return sys.maxsize
            if self._are_nodes_consecutive_depos(_from_node, _to_node):
                return sys.maxsize
            if _from_node in self._reloading_virtual_depos_indices:
                vehicle_of_node = self._vehicle_per_reloading_depot[_from_node]
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
                _from_node = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            elif _to_node in self._reloading_virtual_depos_indices:
                vehicle_of_node = self._vehicle_per_reloading_depot[_to_node]
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
                _to_node = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            graph_travel_time = self._travel_time_matrix[_from_node][_to_node]
            return graph_travel_time

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

        @lru_cache()
        def travel_time_evaluator(_from_index, _to_index):
            return _travel_time[self._index_manager.index_to_node(_from_index)][self._index_manager.index_to_node(
                _to_index)]

        return travel_time_evaluator

    def _create_session_evaluator(self):

        def session_time(_from_node, _to_node):
            if _from_node == _to_node:
                return 0
            if _from_node in self._arrive_indices and _to_node == (_from_node + 1):
                return -self._matcher_input.config.constraints.session_time.max_session_time
            if _from_node in self._arrive_indices and _to_node != (_from_node + 1):
                return sys.maxsize
            if _to_node in self._depart_indices and _from_node != (_to_node - 1):
                return sys.maxsize
            if self._are_nodes_consecutive_depos(_from_node, _to_node):
                return sys.maxsize
            if _from_node in self._reloading_virtual_depos_indices:
                vehicle_of_node = self._vehicle_per_reloading_depot[_from_node]
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
                _from_node = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            elif _to_node in self._reloading_virtual_depos_indices:
                vehicle_of_node = self._vehicle_per_reloading_depot[_to_node]
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
                _to_node = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            graph_session_time = self._travel_time_matrix[_from_node][_to_node]
            return graph_session_time

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

        @lru_cache()
        def session_evaluator(_from_index, _to_index):
            return _session_time[self._index_manager.index_to_node(_from_index)][self._index_manager.index_to_node(
                _to_index)]

        return session_evaluator

    def _create_demand_evaluator(self, package_type: PackageType):

        def _get_package_amount_by_type(_from_node: np.int64, _package_type: PackageType) -> int:
            if _from_node in self._depart_indices:
                package_amount_by_type = -1 * max(
                    self._matcher_input.delivering_drones_board.get_package_type_amount_per_drone_delivery(_package_type))
            elif _from_node in self._arrive_indices:
                package_amount_by_type = 0
            else:
                package_amount_by_type = self._graph_exporter.export_package_type_demands(self._matcher_input.graph,
                                                                                          _package_type)[_from_node]
            return package_amount_by_type

        setattr(self, "_demands_" + str.lower(package_type.name), {})
        _demands = getattr(self, "_demands_" + str.lower(package_type.name))
        for from_node in range(self._num_of_nodes):
            _demands[from_node] = int(_get_package_amount_by_type(from_node, package_type))

        @lru_cache()
        def _get_tiny_demand_callback(_from_index: np.int64) -> int:
            return self._demands_tiny[self._index_manager.index_to_node(_from_index)]

        @lru_cache()
        def _get_small_demand_callback(_from_index: np.int64) -> int:
            return self._demands_small[self._index_manager.index_to_node(_from_index)]

        @lru_cache()
        def _get_medium_demand_callback(_from_index: np.int64) -> int:
            return self._demands_medium[self._index_manager.index_to_node(_from_index)]

        @lru_cache()
        def _get_large_demand_callback(_from_index: np.int64) -> int:
            return self._demands_large[self._index_manager.index_to_node(_from_index)]

        demand_evaluators = {
            PackageType.TINY: _get_tiny_demand_callback,
            PackageType.SMALL: _get_small_demand_callback,
            PackageType.MEDIUM: _get_medium_demand_callback,
            PackageType.LARGE: _get_large_demand_callback
        }

        return demand_evaluators[package_type]

    def _are_nodes_consecutive_depos(self, from_node, to_node) -> bool:
        return from_node in self._depos and to_node in self._depos

    def _set_max_route_time_for_each_vehicle(self, time_dimension: RoutingDimension):
        for i, drone_delivery in enumerate(self._matcher_input.delivering_drones_board.delivering_drones_list):
            max_route_time_in_minutes = drone_delivery.max_route_time_in_minutes
            time_dimension.SetSpanUpperBoundForVehicle(max_route_time_in_minutes, i)
