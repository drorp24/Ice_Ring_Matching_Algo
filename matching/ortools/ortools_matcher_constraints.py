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


class OrToolsDimensionDescription(Enum):
    capacity = "capacity"
    travel_cost = "travel_cost"
    travel_time = "travel_time"
    session_time = "session_time"


class ORToolsMatcherConstraints:
    def __init__(self, index_manager: RoutingIndexManager, routing_model: RoutingModel,
                 matcher_input: MatcherInput, reloading_virtual_depos_indices: [int], reload_time_in_minutes: int):
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input
        self._travel_cost_matrix = self._graph_exporter.export_travel_costs(self._matcher_input.graph)
        self._travel_time_matrix = self._graph_exporter.export_travel_times(self._matcher_input.graph)
        self._time_windows = self._graph_exporter.export_time_windows(self._matcher_input.graph,
                                                                      self._matcher_input.config.zero_time)

        self._basis_nodes_indices = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)
        self._reloading_virtual_depos_indices = reloading_virtual_depos_indices
        self._reload_time_in_minutes = reload_time_in_minutes
        self._depos = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph) \
                      + self._reloading_virtual_depos_indices
        self._num_of_nodes = len(self._depos) + len(self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph))

    def add_travel_cost(self):
        travel_cost_callback_index = self._routing_model.RegisterTransitCallback(self._get_travel_cost_callback)
        self._routing_model.AddDimension(
            travel_cost_callback_index,
            0,
            MAX_OPERATION_TIME,
            True,
            OrToolsDimensionDescription.travel_cost.value)
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_cost.value)
        # self._add_time_window_constraints_for_each_delivery_except_depot(travel_time_dimension, self._time_windows)
        # self._add_time_window_constraints_for_each_vehicle_start_node(travel_time_dimension, self._time_windows)
        # travel_time_dimension.SetGlobalSpanCostCoefficient(100)
        # self._instantiate_route_start_and_end_times_to_produce_feasible_times(travel_time_dimension)
        for node in range(self._num_of_nodes):
            index = self._index_manager.NodeToIndex(node)
            # if node in [37, 39, 41]:
            #     travel_time_dimension.SlackVar(index).SetMin(60)
            if node in [36, 38, 40]:
                travel_time_dimension.SlackVar(index).SetValue(0)
            elif node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
                    # or node in self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph):
                travel_time_dimension.SlackVar(index).SetValue(0)
        # for node in self._reloading_virtual_depos_indices:
        #     travel_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetMin(60)
        # for node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
        #     travel_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetValue(0)
        # for node in self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph):
        #     travel_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetValue(0)
        # for node in range(self._routing_model.Size()):
            self._routing_model.AddToAssignment(travel_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(travel_time_dimension.SlackVar(index))
        for vehicle_id in range(self._matcher_input.empty_board.amount_of_formations()):
            # session_time_dimension.SetSpanCostCoefficientForVehicle(120, vehicle_id)
            index = self._routing_model.Start(vehicle_id)
            self._routing_model.AddToAssignment(travel_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(travel_time_dimension.SlackVar(index))

    def add_travel_time(self):
        travel_time_callback_index = self._routing_model.RegisterTransitCallback(self._get_travel_time_callback)
        self._routing_model.AddDimension(
            travel_time_callback_index,
            MAX_OPERATION_TIME, #self._matcher_input.config.constraints.time.max_waiting_time,
            MAX_OPERATION_TIME,
            self._matcher_input.config.constraints.time.count_time_from_zero,
            OrToolsDimensionDescription.travel_time.value)
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        self._add_time_window_constraints_for_each_delivery_except_depot(travel_time_dimension, self._time_windows)
        self._add_time_window_constraints_for_each_vehicle_start_node(travel_time_dimension, self._time_windows)
        # travel_time_dimension.SetSpanCostCoefficientForAllVehicles(1)
        # self._instantiate_route_start_and_end_times_to_produce_feasible_times(travel_time_dimension)
        # travel_time_dimension.SetGlobalSpanCostCoefficient(1)
        for node in range(self._num_of_nodes):
            index = self._index_manager.NodeToIndex(node)
            # if node in [37, 39, 41]:
            #     travel_time_dimension.SlackVar(index).SetMin(60)
            # if node in [36, 38, 40]:
            #     travel_time_dimension.SlackVar(index).SetValue(0)
            # if node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
            #         # or node in self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph):
            #     travel_time_dimension.SlackVar(index).SetValue(0)
        # for node in self._reloading_virtual_depos_indices:
        #     travel_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetMin(60)
        # for node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
        #     travel_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetValue(0)
        # for node in self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph):
        #     travel_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetValue(0)
        # for node in range(self._routing_model.Size()):
            self._routing_model.AddToAssignment(travel_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(travel_time_dimension.SlackVar(index))
        for vehicle_id in range(self._matcher_input.empty_board.amount_of_formations()):
            # session_time_dimension.SetSpanCostCoefficientForVehicle(120, vehicle_id)
            index = self._routing_model.Start(vehicle_id)
            self._routing_model.AddToAssignment(travel_time_dimension.TransitVar(index))
            self._routing_model.AddToAssignment(travel_time_dimension.SlackVar(index))

    def add_session_time(self):
        session_time_callback_index = self._routing_model.RegisterTransitCallback(self._get_session_time_callback)
        self._routing_model.AddDimension(
            session_time_callback_index,
            180,
            180,
            True,
            OrToolsDimensionDescription.session_time.value)
        session_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.session_time.value)
        for node in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
            session_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetValue(0)
        # for node in [36,38,40]:
        #     session_time_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetValue(0)


    # def add_session_time(self):
    #     session_time_callback_index = self._routing_model.RegisterTransitCallback(self._get_session_time_callback)
    #     self._routing_model.AddDimension(
    #         session_time_callback_index,
    #         90,# self._matcher_input.config.constraints.time.max_waiting_time,
    #         90,
    #         False,  # self._matcher_input.config.constraints.time.count_time_from_zero,
    #         OrToolsDimensionDescription.session_time.value)
    #
    #     session_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.session_time.value)
    #     # travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
    #     # self._reset_demand_nodes_slack(OrToolsDimensionDescription.session_time.value)
    #     # self._set_max_session_time(session_time_dimension)
    #     for node in range(self._num_of_nodes):
    #         index = self._index_manager.NodeToIndex(node)
    #         if node not in self._depos:
    #             session_time_dimension.SlackVar(index).SetValue(0)
    #         self._routing_model.AddToAssignment(session_time_dimension.TransitVar(index))
    #         self._routing_model.AddToAssignment(session_time_dimension.SlackVar(index))
    #
    #     # for node in self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph):
    #     #     index = self._index_manager.NodeToIndex(node)
    #     #     session_time_dimension.SlackVar(index).SetValue(0)
    #     for vehicle_id in range(self._matcher_input.empty_board.amount_of_formations()):
    #         # session_time_dimension.SetSpanCostCoefficientForVehicle(120, vehicle_id)
    #         index = self._routing_model.Start(vehicle_id)
    #         # session_time_dimension.SlackVar(index).SetValue(0)
    #         self._routing_model.AddToAssignment(session_time_dimension.TransitVar(index))
    #         self._routing_model.AddToAssignment(session_time_dimension.SlackVar(index))
    #         # self._routing_model.AddVariableMinimizedByFinalizer(session_time_dimension.CumulVar(node))
    #
    #         # else:
    #         #     self._routing_model.AddVariableMinimizedByFinalizer(session_time_dimension.CumulVar(node))
    #
    #         # self._routing_model.AddVariableMinimizedByFinalizer(session_time_dimension.CumulVar(node))
    #         # session_time_dimension.CumulVar(node).SetRange(0, 120)

    def add_demand(self):
        demand_dimension_name_prefix = OrToolsDimensionDescription.capacity.value + "_"
        for package_type in self._matcher_input.empty_board.package_types():
            demand_dimension_name = demand_dimension_name_prefix + str.lower(package_type.name)
            callback = getattr(self, "_get_" + str.lower(package_type.name) + "_demand_callback")
            demand_callback_index = self._routing_model.RegisterPositiveUnaryTransitCallback(callback)
            self._routing_model.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                MAX_DEMAND_RELOAD,
                self._matcher_input.empty_board.get_package_type_amount_per_drone_delivery(package_type),
                self._matcher_input.config.constraints.capacity.count_capacity_from_zero,
                demand_dimension_name)
            self._reset_demand_nodes_slack(demand_dimension_name)

    def add_unmatched_penalty(self):
        for node in range(1, len(self._matcher_input.graph.nodes)):
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
        # if from_node in [37, 39, 41]:
        #     return 0
        if from_node in self._reloading_virtual_depos_indices:#[36, 38, 40]:
            return -MAX_DEMAND_RELOAD #-1 * max(self._matcher_input.empty_board.get_package_type_amount_per_drone_delivery(package_type))
        # if from_node in self._reloading_virtual_depos_indices:
        #     return -1 * max(self._matcher_input.empty_board.get_package_type_amount_per_drone_delivery(package_type))
        return self._graph_exporter.export_package_type_demands(self._matcher_input.graph, package_type)[from_node]

    def _reset_demand_nodes_slack(self, demand_dimension_name: str):
        demand_dimension = self._routing_model.GetDimensionOrDie(demand_dimension_name)
        for node in range(1, len(self._matcher_input.graph.nodes)):
            demand_dimension.SlackVar(self._index_manager.NodeToIndex(node)).SetValue(0)

    # def _instantiate_route_start_and_end_times_to_produce_feasible_times(self, time_dimension: RoutingDimension):
    #     for i in range(len(self._matcher_input.empty_board.empty_drone_deliveries)):
    #         self._routing_model.AddVariableMinimizedByFinalizer(
    #             time_dimension.CumulVar(self._routing_model.Start(i)))
    #         self._routing_model.AddVariableMinimizedByFinalizer(
    #             time_dimension.CumulVar(self._routing_model.End(i)))
    #     #
    #     # for node in self._reloading_virtual_depos_indices:
    #     #     node_index = self._index_manager.NodeToIndex(node)
    #     #     self._routing_model.AddVariableMinimizedByFinalizer(
    #     #         time_dimension.CumulVar(node_index))
    #
    #     # for i in range(self._routing_model.Size()):
    #     #     self._routing_model.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(i))
    # #     self._routing_model.AddVariableMinimizedByFinalizer(
    # #         time_dimension.CumulVar(self._routing_model.Start(i)))
    def _add_time_window_constraints_for_each_vehicle_start_node(self, time_dimension: RoutingDimension,
                                                                 time_windows: List[Tuple[int, int]]):
        for i, drone_delivery in enumerate(self._matcher_input.empty_board.empty_drone_deliveries):
            start_index = self._routing_model.Start(i)
            graph_index = self._index_manager.IndexToNode(start_index)
            time_dimension.CumulVar(start_index).SetRange(time_windows[graph_index][0],
                                                          time_windows[graph_index][1])

    # def _set_max_session_time(self, session_time_dimension: RoutingDimension):
    #     # for node in range(1, len(self._matcher_input.graph.nodes)):
    #     #     session_time_dimension.SetCumulVarSoftUpperBound(self._index_manager.NodeToIndex(node), 120, 1000)
    #     for node in self._reloading_virtual_depos_indices:
    #         session_time_dimension.CumulVar(self._index_manager.NodeToIndex(node)).SetMax(180)
    #     # session_time_dimension.SetCumulVarSoftUpperBound(120, i)
    #     # for i, drone_delivery in enumerate(self._matcher_input.empty_board.empty_drone_deliveries):
    #     #     max_route_time_in_minutes = drone_delivery.max_route_time_in_minutes
    #     #     session_time_dimension.SetCumulVarSoftUpperBound(120, i)

    def _add_time_window_constraints_for_each_delivery_except_depot(self, time_dimension: RoutingDimension,
                                                                    time_windows: List[Tuple[int, int]]):
        for graph_index, time_window in enumerate(time_windows):
            if graph_index in self._basis_nodes_indices:
                continue
            index = self._index_manager.NodeToIndex(graph_index)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        # for node in self._reloading_virtual_depos_indices:
        #     index = self._index_manager.NodeToIndex(node)
        #     time_dimension.CumulVar(index).SetRange(self._time_windows[0][0], self._time_windows[0][1])

    def _get_travel_cost_callback(self, from_index: np.int64, to_index: np.int64) -> np.int64:
        from_node = self._index_manager.IndexToNode(from_index)
        to_node = self._index_manager.IndexToNode(to_index)
        if from_node == to_node:
            return 0
        if from_node in [36, 38, 40] and to_node == from_node + 1:
            return 0
        if from_node in [36, 38, 40] and to_node != from_node + 1:
            return sys.maxsize
        if to_node in [37, 39, 41] and from_node != to_node - 1:
            return sys.maxsize
        if self._are_nodes_consecutive_depos(from_node, to_node):
            return sys.maxsize
        if from_node in self._reloading_virtual_depos_indices:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[0][to_node]}')
            from_node = 0
        elif to_node in self._reloading_virtual_depos_indices:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[from_node][0]}')
            to_node = 0
        # else:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[from_node][to_node]}')
        travel_time = self._travel_cost_matrix[from_node][to_node]
        # if travel_time < 0:
        #     print(f'TRAVEL IS NEGETIVE!!!! {travel_time}')
        return travel_time

    #     from_node = self._index_manager.IndexToNode(from_index)
    #     to_node = self._index_manager.IndexToNode(to_index)
    #     if self._are_nodes_consecutive_depos(from_node, to_node):
    #         return sys.maxsize
    #     else:
    #         if from_node in self._reloading_virtual_depos_indices:
    #             from_node = 0
    #         if to_node in self._reloading_virtual_depos_indices:
    #             to_node = 0
    #         return self._travel_cost_matrix[from_node][to_node]
    #
    def _get_travel_time_callback(self, from_index: np.int64, to_index: np.int64) -> np.int64:
        from_node = self._index_manager.IndexToNode(from_index)
        to_node = self._index_manager.IndexToNode(to_index)
        if from_node == to_node:
            return 0
        if from_node in [36, 38, 40] and to_node == from_node + 1:
            return 0
        if from_node in [36, 38, 40] and to_node != from_node + 1:
            return sys.maxsize
        if to_node in [37, 39, 41] and from_node != to_node - 1:
            return sys.maxsize
        if self._are_nodes_consecutive_depos(from_node, to_node):
            return sys.maxsize
        if from_node in self._reloading_virtual_depos_indices:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[0][to_node]}')
            from_node = 0
        elif to_node in self._reloading_virtual_depos_indices:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[from_node][0]}')
            to_node = 0
        # else:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[from_node][to_node]}')
        travel_time = self._travel_time_matrix[from_node][to_node]
        # if travel_time < 0:
        #     print(f'TRAVEL IS NEGETIVE!!!! {travel_time}')
        return travel_time

    #     from_node = self._index_manager.IndexToNode(from_index)
    #     to_node = self._index_manager.IndexToNode(to_index)
    #     if self._are_nodes_consecutive_depos(from_node, to_node):
    #         return sys.maxsize
    #     if from_node in self._reloading_virtual_depos_indices:
    #         from_node = 0
    #     if to_node in self._reloading_virtual_depos_indices:
    #         to_node = 0
    #     travel_time = self._travel_time_matrix[from_node][to_node]
    #     if travel_time < 0:
    #         print(f'TRAVEL IS NEGETIVE!!!! {travel_time}')
    #     return travel_time

    def _get_session_time_callback(self, from_index: np.int64, to_index: np.int64) -> np.int64:
        from_node = self._index_manager.IndexToNode(from_index)
        to_node = self._index_manager.IndexToNode(to_index)
        # print(f'from_node {from_node} to_node {to_node}')# travel_time {self._travel_time_matrix[0][to_node]}')
        if from_node == to_node:
            return 0
        if from_node in [36, 38, 40] and to_node == from_node + 1:
            return -180
        if from_node in [36, 38, 40] and to_node != from_node + 1:
            return sys.maxsize
        if to_node in [37, 39, 41] and from_node != to_node - 1:
            return sys.maxsize
        if self._are_nodes_consecutive_depos(from_node, to_node):
            return sys.maxsize
        if from_node in self._reloading_virtual_depos_indices:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[0][to_node]}')
            from_node = 0
        elif to_node in self._reloading_virtual_depos_indices:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[from_node][0]}')
            to_node = 0
        # else:
            # print(f'from_node {from_node} to_node {to_node} travel_time {self._travel_time_matrix[from_node][to_node]}')
        travel_time = self._travel_time_matrix[from_node][to_node]
        # if travel_time < 0:
        #     print(f'TRAVEL IS NEGETIVE!!!! {travel_time}')
        return travel_time

    def _are_nodes_consecutive_depos(self, from_node, to_node) -> bool:
        return from_node in self._depos and to_node in self._depos
