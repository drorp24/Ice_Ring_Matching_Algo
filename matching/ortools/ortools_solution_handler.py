from datetime import timedelta
from typing import List
from ortools.constraint_solver.pywrapcp import Assignment, RoutingModel

from common.entities.base_entities.drone_delivery import DroneDelivery, MatchedDeliveryRequest, MatchedDroneLoadingDock
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.temporal import TimeWindowExtension, TimeDeltaExtension
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.initial_solution import Routes, Route
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_index_manager_wrapper import OrToolsIndexManagerWrapper
from matching.ortools.ortools_matcher_constraints import OrToolsDimensionDescription


class ORToolsSolutionHandler:
    def __init__(self, graph_exporter: OrtoolsGraphExporter, index_manager: OrToolsIndexManagerWrapper,
                 routing_model: RoutingModel, matcher_input: MatcherInput,
                 reloading_depos_arrive_indices: [int], reloading_depos_depart_indices: [int],
                 reloading_depots_per_vehicle: {}, vehicle_per_reloading_depot: {},
                 start_depots_graph_indices: [int], end_depots_graph_indices: [int]):
        self._graph_exporter = graph_exporter
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input
        self._arrive_indices = reloading_depos_arrive_indices
        self._depart_indices = reloading_depos_depart_indices
        self._reloading_virtual_depos_indices = self._arrive_indices + self._depart_indices
        self._depos = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph) \
            + self._reloading_virtual_depos_indices
        self._num_of_nodes = len(self._matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)
        self._travel_time_matrix = self._graph_exporter.export_travel_times(self._matcher_input.graph)
        self._reloading_depots_per_vehicle = reloading_depots_per_vehicle
        self._vehicle_per_reloading_depot = vehicle_per_reloading_depot
        self._start_depots_graph_indices = start_depots_graph_indices
        self._end_depots_graph_indices = end_depots_graph_indices

    def create_drone_delivery_board(self, solution: Assignment) -> DroneDeliveryBoard:

        return DroneDeliveryBoard(drone_deliveries=self._create_drone_deliveries(solution),
                                  unmatched_delivery_requests=self._extract_unmatched_delivery_requests(solution))

    def get_routes(self, solution: Assignment) -> Routes:
        if solution is None:
            return Routes([])

        routes = []
        for delivering_drones_index, delivering_drones in enumerate(self._matcher_input.delivering_drones_board.delivering_drones_list):
            index = self._routing_model.Start(delivering_drones_index)
            route = []
            while not self._routing_model.IsEnd(index):
                if not self._routing_model.IsStart(index):
                    route.append(index)
                index = solution.Value(self._routing_model.NextVar(index))

            routes.append(Route(route))
        return Routes(routes)

    def _create_drone_deliveries(self, solution: Assignment) -> List[DroneDelivery]:
        if solution is None:
            return []
        drone_deliveries = []
        for delivering_drones_index, delivering_drones in enumerate(self._matcher_input.delivering_drones_board.delivering_drones_list):
            # self._print_solution_debug_info(delivering_drones_index, solution)
            start_index = self._routing_model.Start(delivering_drones_index)
            graph_start_index = self._index_manager.index_to_node(start_index)
            vehicle_of_node = self._start_depots_graph_indices.index(graph_start_index)
            dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
            start_drone_loading_dock = self._create_start_drone_loading_dock(dock, start_index, solution)
            index = solution.Value(self._routing_model.NextVar(start_index))
            matched_requests = []
            while not self._routing_model.IsEnd(index) and not self._routing_model.IsStart(index):
                graph_index = self._index_manager.index_to_node(index)
                if graph_index in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
                    matched_requests.append(
                        self._create_matched_delivery_request(graph_index, index, solution))
                elif graph_index in self._arrive_indices:
                    vehicle_of_node = self._vehicle_per_reloading_depot[graph_index]
                    dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].end_loading_dock
                    end_drone_loading_dock = self._create_end_drone_loading_dock(dock, index, solution)
                    drone_deliveries.append(
                        self._create_drone_delivery(delivering_drones_index, start_drone_loading_dock, end_drone_loading_dock,
                                                    matched_requests))
                    matched_requests = []
                elif graph_index in self._depart_indices:
                    vehicle_of_node = self._vehicle_per_reloading_depot[graph_index]
                    dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].start_loading_dock
                    start_drone_loading_dock = self._create_start_drone_loading_dock(
                        dock, index, solution)
                index = solution.Value(self._routing_model.NextVar(index))
            if self._routing_model.IsEnd(index):
                graph_index = self._index_manager.index_to_node(index)
                vehicle_of_node = self._end_depots_graph_indices.index(graph_index)
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[vehicle_of_node].end_loading_dock
                end_drone_loading_dock = self._create_end_drone_loading_dock(dock, index, solution)
                drone_deliveries.append(
                    self._create_drone_delivery(delivering_drones_index, start_drone_loading_dock, end_drone_loading_dock,
                                                matched_requests))
        return drone_deliveries

    def _print_solution_debug_info(self, delivering_drones_index, solution):
        if solution:
            print(f'Objective: {solution.ObjectiveValue()}')
        time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        demand_dimension = self._routing_model.GetDimensionOrDie("capacity_large")
        index = self._routing_model.Start(delivering_drones_index)
        plan_output = f'DEBUG Route for vehicle {delivering_drones_index}:\n'
        while not self._routing_model.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            time_var_transit = time_dimension.TransitVar(index)
            time_var_slack = time_dimension.SlackVar(index)
            demand_var = demand_dimension.CumulVar(index)
            demand_var_transit = demand_dimension.TransitVar(index)
            demand_var_slack = demand_dimension.SlackVar(index)
            plan_output += f' {self._index_manager.index_to_node(index)} ' \
                           f'Time({solution.Min(time_var)},{solution.Max(time_var)}) ' \
                           f'Transit({solution.Min(time_var_transit)},{solution.Max(time_var_transit)}) ' \
                           f'Slack({solution.Min(time_var_slack)},{solution.Max(time_var_slack)}) ' \
                           f'Demand({solution.Min(demand_var)},{solution.Max(demand_var)}) ' \
                           f'Demand_Transit({solution.Min(demand_var_transit)},{solution.Max(demand_var_transit)}) ' \
                           f'Demand_Slack({solution.Min(demand_var_slack)},{solution.Max(demand_var_slack)}) ' \
                           ') ->'
            index = solution.Value(self._routing_model.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += f' {self._index_manager.index_to_node(index)} ' \
                       f'Time({solution.Min(time_var)},{solution.Max(time_var)}) '
        print(plan_output)

    def _extract_unmatched_delivery_requests(self, solution: Assignment) -> List[UnmatchedDeliveryRequest]:
        if solution is None:
            return []
        unmatched_delivery_request = []
        for index in range(self._num_of_nodes):
            if self._routing_model.IsStart(index) or self._routing_model.IsEnd(
                    index) or index in self._reloading_virtual_depos_indices:
                continue
            if solution.Value(self._routing_model.NextVar(index)) == index:
                graph_index = self._index_manager.index_to_node(index)
                unmatched_delivery_request.append(UnmatchedDeliveryRequest(
                    graph_index=graph_index,
                    delivery_request=self._graph_exporter.get_delivery_request(
                        self._matcher_input.graph, graph_index)))

        return unmatched_delivery_request

    def _create_drone_delivery(self, delivering_drones_index: int, start_drone_loading_dock: MatchedDroneLoadingDock,
                               end_drone_loading_dock: MatchedDroneLoadingDock,
                               matched_requests: List[MatchedDeliveryRequest]) -> DroneDelivery:
        return DroneDelivery(self._matcher_input.delivering_drones_board.delivering_drones_list[delivering_drones_index],
                             matched_requests, start_drone_loading_dock, end_drone_loading_dock)

    def _create_matched_delivery_request(self, graph_index: int, index: int,
                                         solution: Assignment) -> MatchedDeliveryRequest:
        if solution is None:
            raise ValueError('No Solution!')
        return MatchedDeliveryRequest(
            graph_index=graph_index,
            delivery_request=self._graph_exporter.get_delivery_request(
                self._matcher_input.graph,
                graph_index),
            matched_delivery_option_index=0,
            delivery_time_window=self._get_delivery_time_window(index, solution))

    def _create_start_drone_loading_dock(self, loading_dock: DroneLoadingDock, index: int,
                                         solution: Assignment) -> MatchedDroneLoadingDock:
        if solution is None:
            raise ValueError('No Solution!')

        delivery_time_window = self._get_start_dock_time_window(loading_dock, index, solution)
        return MatchedDroneLoadingDock(
            drone_loading_dock=loading_dock,
            delivery_time_window=delivery_time_window)

    def _create_end_drone_loading_dock(self, loading_dock: DroneLoadingDock, index: int,
                                       solution: Assignment) -> MatchedDroneLoadingDock:
        if solution is None:
            raise ValueError('No Solution!')

        delivery_time_window = self._get_delivery_time_window(index, solution)
        return MatchedDroneLoadingDock(
            drone_loading_dock=loading_dock,
            delivery_time_window=delivery_time_window)

    def _get_delivery_time_window(self, index: int, solution: Assignment, service_time_in_min=0) -> TimeWindowExtension:
        if solution is None:
            raise ValueError('No Solution!')
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        travel_time_var = travel_time_dimension.CumulVar(index)

        return TimeWindowExtension(
            since=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Min(travel_time_var) + service_time_in_min)))),
            until=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Max(travel_time_var) + service_time_in_min)))))

    def _get_start_dock_time_window(self, loading_dock: DroneLoadingDock, index, solution):
        first_delivery_index = solution.Value(self._routing_model.NextVar(index))
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        first_delivery_min_arrival_time = solution.Min(travel_time_dimension.CumulVar(first_delivery_index))
        graph_index = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, loading_dock)
        travel_time_from_dock_to_first_delivery_in_min = \
            self._travel_time_matrix[graph_index][self._index_manager.index_to_node(first_delivery_index)]
        service_time_in_min = float(first_delivery_min_arrival_time
                                    - travel_time_from_dock_to_first_delivery_in_min)
        return TimeWindowExtension(
            since=self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=service_time_in_min))),
            until=self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=service_time_in_min))))
