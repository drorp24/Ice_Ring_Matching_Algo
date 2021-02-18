from datetime import timedelta
from typing import List

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel, Assignment
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from common.entities.base_entities.drone_delivery import DroneDelivery, MatchedDroneLoadingDock, MatchedDeliveryRequest
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.temporal import TimeDeltaExtension, TimeWindowExtension
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import Matcher
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher_constraints import ORToolsMatcherConstraints, OrToolsDimensionDescription
from matching.ortools.ortools_matcher_objective import ORToolsMatcherObjective

AVERAGE_RELOAD_PER_FORMATION = 3


class ORToolsMatcher(Matcher):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)
        self._reloading_virtual_depos_indices = list(range(
            len(self._matcher_input.graph.nodes),
            len(self._matcher_input.graph.nodes)
            + self._matcher_input.empty_board.amount_of_formations() * AVERAGE_RELOAD_PER_FORMATION))
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = self._set_index_manager()
        self._routing_model = self._set_routing_model()
        self._search_parameters = self._set_search_params()

        self._set_objective()
        self._set_constraints()

    def match(self) -> DroneDeliveryBoard:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        return self._create_drone_delivery_board(solution)

    def _set_index_manager(self) -> RoutingIndexManager:
        num_vehicles = self._matcher_input.empty_board.amount_of_formations()
        depot_ids_start = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)
        # TODO depot_ids_end = self._graph_exporter.export_basis_nodes_indices(self._match_input.graph)
        num_of_nodes = len(self.matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)
        manager = pywrapcp.RoutingIndexManager(num_of_nodes,
                                               num_vehicles,
                                               depot_ids_start[0])
        # TODO add depot_ids_end as forth param)

        return manager

    def _set_routing_model(self) -> RoutingModel:
        return pywrapcp.RoutingModel(self._index_manager)

    def _set_objective(self):
        ORToolsMatcherObjective(self._index_manager, self._routing_model, self.matcher_input,
                                self._reloading_virtual_depos_indices).add_priority()

    def _set_search_params(self) -> RoutingSearchParameters:

        self._search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        self._search_parameters.first_solution_strategy = \
            self.matcher_input.config.solver.get_first_solution_strategy_as_int()

        self._search_parameters.local_search_metaheuristic = \
            self.matcher_input.config.solver.get_local_search_strategy_as_int()

        self._search_parameters.time_limit.seconds = self.matcher_input.config.solver.timeout_sec

        return self._search_parameters

    def _set_constraints(self):
        matcher_constraints = ORToolsMatcherConstraints(self._index_manager, self._routing_model, self.matcher_input,
                                                        self._reloading_virtual_depos_indices, 60)
        #  TODO: should be reload depos for every formation type (size and package)
        matcher_constraints.add_demand()
        matcher_constraints.add_travel_cost()
        matcher_constraints.add_travel_time()
        matcher_constraints.add_session_time()
        matcher_constraints.add_unmatched_penalty()

    def _create_drone_delivery_board(self, solution: Assignment) -> DroneDeliveryBoard:
        return DroneDeliveryBoard(drone_deliveries=self._create_drone_deliveries(solution),
                                  unmatched_delivery_requests=self._extract_unmatched_delivery_requests(solution))

    def _create_drone_deliveries(self, solution: Assignment) -> List[DroneDelivery]:
        if solution is None:
            return []
        drone_deliveries = []
        for edd_index, empty_drone_delivery in enumerate(self.matcher_input.empty_board.empty_drone_deliveries):
            #
            # # capacity_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.capacity.value)
            # time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
            # # fuel_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.session_time.value)
            # index = self._routing_model.Start(edd_index)
            # plan_output = f'DEBUG Route for vehicle {edd_index}:\n'
            # distance = 0
            # while not self._routing_model.IsEnd(index):
            #     # load_var = capacity_dimension.CumulVar(index)
            #     time_var = time_dimension.CumulVar(index)
            #     time_var_transit = time_dimension.TransitVar(index)
            #     time_var_slack = time_dimension.SlackVar(index)
            #     # fuel_var = fuel_dimension.CumulVar(index)
            #     # fuel_var_transit = fuel_dimension.TransitVar(index)
            #     # fuel_var_slack = fuel_dimension.SlackVar(index)
            #     plan_output += f' {self._index_manager.IndexToNode(index)} ' \
            #                    f'Time({solution.Min(time_var)},{solution.Max(time_var)}) ' \
            #                    f'Transit({solution.Min(time_var_transit)},{solution.Max(time_var_transit)}) ' \
            #                    f'Slack({solution.Min(time_var_slack)},{solution.Max(time_var_slack)}) ) ->'
            #                    # f'Fuel({solution.Min(fuel_var)},{solution.Max(fuel_var)}) ' \
            #                    # f'Transit({solution.Min(fuel_var_transit)},{solution.Max(fuel_var_transit)}) ' \
            #                    # f'Slack({solution.Min(fuel_var_slack)},{solution.Max(fuel_var_slack)}) ) ->'
            #     index = solution.Value(self._routing_model.NextVar(index))
            # time_var = time_dimension.CumulVar(index)
            # # fuel_var = fuel_dimension.CumulVar(index)
            # plan_output += f' {self._index_manager.IndexToNode(index)} ' \
            #                f'Time({solution.Min(time_var)},{solution.Max(time_var)}) '
            #                # f'Fuel({solution.Min(fuel_var)},{solution.Max(fuel_var)}) '
            # print(plan_output)

            start_index = self._routing_model.Start(edd_index)
            graph_start_index = self._index_manager.IndexToNode(start_index)
            start_drone_loading_dock = self._create_drone_loading_dock(graph_start_index, start_index, solution, 1)
            index = solution.Value(self._routing_model.NextVar(start_index))
            matched_requests = []
            while not self._routing_model.IsEnd(index) and not self._routing_model.IsStart(index):
                graph_index = self._index_manager.IndexToNode(index)
                if graph_index in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
                    matched_requests.append(
                        self._create_matched_delivery_request(graph_index, index, solution))
                if graph_index in [36, 38, 40]:#self._reloading_virtual_depos_indices:
                    graph_index = 0
                    end_drone_loading_dock = self._create_drone_loading_dock(graph_index, index, solution)
                    drone_deliveries.append(
                        self._create_drone_delivery(edd_index, start_drone_loading_dock, end_drone_loading_dock,
                                                    matched_requests))
                    matched_requests = []
                if graph_index in [37, 39, 41]:  # self._reloading_virtual_depos_indices:
                    graph_index = 0
                    start_drone_loading_dock = self._create_drone_loading_dock(
                        graph_index, index, solution,
                        empty_drone_delivery.reload_time_in_minutes)
                index = solution.Value(self._routing_model.NextVar(index))
            if self._routing_model.IsEnd(index):
                graph_index = self._index_manager.IndexToNode(index)
                end_drone_loading_dock = self._create_drone_loading_dock(graph_index, index, solution)
                drone_deliveries.append(
                    self._create_drone_delivery(edd_index, start_drone_loading_dock, end_drone_loading_dock,
                                                matched_requests))
        return drone_deliveries

    def _extract_unmatched_delivery_requests(self, solution: Assignment) -> List[UnmatchedDeliveryRequest]:
        if solution is None:
            return []
        unmatched_delivery_request = []
        for index in range(self._routing_model.Size()):
            if self._routing_model.IsStart(index) or self._routing_model.IsEnd(
                    index) or index in self._reloading_virtual_depos_indices:
                continue
            if solution.Value(self._routing_model.NextVar(index)) == index:
                graph_index = self._index_manager.IndexToNode(index)
                unmatched_delivery_request.append(UnmatchedDeliveryRequest(
                    graph_index=graph_index,
                    delivery_request=self._graph_exporter.get_delivery_request(
                        self.matcher_input.graph, graph_index)))

        return unmatched_delivery_request

    # def _create_matched_delivery_requests(self, edd_index: int, solution: Assignment) -> List[MatchedDeliveryRequest]:
    #     if solution is None:
    #         return []
    #     matched_requests = []
    #     start_index = self._routing_model.Start(edd_index)
    #     index = solution.Value(self._routing_model.NextVar(start_index))
    #     if index in self._reloading_virtual_depos_indices:
    #         index = solution.Value(self._routing_model.NextVar(index))
    #     while not self._routing_model.IsEnd(index) and not self._routing_model.IsStart(index):
    #         graph_index = self._index_manager.IndexToNode(index)
    #         if graph_index in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
    #             matched_requests.append(
    #                 self._create_matched_delivery_request(graph_index, index, solution))
    #         index = solution.Value(self._routing_model.NextVar(index))
    #     return matched_requests

    def _create_drone_delivery(self, edd_index: int, start_drone_loading_dock: MatchedDroneLoadingDock,
                               end_drone_loading_dock: MatchedDroneLoadingDock,
                               matched_requests: List[MatchedDeliveryRequest]) -> DroneDelivery:
        return DroneDelivery(self.matcher_input.empty_board.empty_drone_deliveries[edd_index].id,
                             self.matcher_input.empty_board.empty_drone_deliveries[
                                 edd_index].drone_formation,
                             matched_requests, start_drone_loading_dock, end_drone_loading_dock)

    def _create_matched_delivery_request(self, graph_index: int, index: int,
                                         solution: Assignment) -> MatchedDeliveryRequest:
        if solution is None:
            raise ValueError('No Solution!')
        return MatchedDeliveryRequest(
            graph_index=graph_index,
            delivery_request=self._graph_exporter.get_delivery_request(
                self.matcher_input.graph,
                graph_index),
            matched_delivery_option_index=0,
            delivery_time_window=self._get_delivery_time_window(index, solution))

    # def _create_start_drone_loading_dock(self, edd_index: int, solution: Assignment) -> MatchedDroneLoadingDock:
    #     if solution is None:
    #         raise ValueError('No Solution!')
    #     start_index = self._routing_model.Start(edd_index)
    #     graph_start_index = self._index_manager.IndexToNode(start_index)
    #     return self._create_drone_loading_dock(graph_start_index, start_index, solution)
    #
    # def _create_end_drone_loading_dock(self, edd_index: int, solution: Assignment) -> MatchedDroneLoadingDock:
    #     if solution is None:
    #         raise ValueError('No Solution!')
    #     end_index = self._routing_model.End(edd_index)
    #     graph_end_index = self._index_manager.IndexToNode(end_index)
    #     return self._create_drone_loading_dock(graph_end_index, end_index, solution)

    def _create_drone_loading_dock(self, graph_index: int, index: int,
                                   solution: Assignment, service_time_in_min=0) -> MatchedDroneLoadingDock:
        if solution is None:
            raise ValueError('No Solution!')
        #
        # delivery_time_window = self._get_delivery_time_window(index, solution) \
        #     if service_time_in_min == 0 \
        #     else self._get_reloading_dock_time_window(graph_index, index, solution)

        return MatchedDroneLoadingDock(
            graph_index=graph_index,
            drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                self.matcher_input.graph, graph_index),
            delivery_time_window=self._get_delivery_time_window(index, solution))

    def _get_reloading_dock_time_window(self, graph_index, index, solution):
        first_delivery_index = solution.Value(self._routing_model.NextVar(index))
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        first_delivery_min_arrival_time = solution.Min(travel_time_dimension.CumulVar(first_delivery_index))
        travel_time_from_dock_to_first_delivery_in_min = self._graph_exporter.export_travel_times(
            self._matcher_input.graph)[graph_index][self._index_manager.IndexToNode(first_delivery_index)]
        print(f'travel_time_from_dock_to_first_delivery_in_min: {travel_time_from_dock_to_first_delivery_in_min}')
        service_time_in_min = float(first_delivery_min_arrival_time
                                    - travel_time_from_dock_to_first_delivery_in_min)
        return TimeWindowExtension(
            since=self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=service_time_in_min))),
            until=self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=service_time_in_min))))

    def _get_delivery_time_window(self, index: int, solution: Assignment) -> TimeWindowExtension:
        if solution is None:
            raise ValueError('No Solution!')
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        travel_time_var = travel_time_dimension.CumulVar(index)

        return TimeWindowExtension(
            since=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Min(travel_time_var))))),
            until=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Max(travel_time_var))))))
