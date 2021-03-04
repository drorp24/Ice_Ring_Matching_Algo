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

AVERAGE_RELOAD_PER_FORMATION = 2
NUM_OF_NODES_IN_RELOADING_DEPO = 2 # Reloading depo consists of 2 nodes:
                                        # arrive node & depart node so we can reset the cumulated time between them.


class ORToolsMatcher(Matcher):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)
        num_of_reloading_depo_nodes = self._matcher_input.empty_board.amount_of_formations() \
                                      * AVERAGE_RELOAD_PER_FORMATION * NUM_OF_NODES_IN_RELOADING_DEPO
        self._reloading_virtual_depos_indices = list(range(
            len(self._matcher_input.graph.nodes),
            len(self._matcher_input.graph.nodes) + num_of_reloading_depo_nodes))
        self._arrive_indices = self._reloading_virtual_depos_indices[0::2]
        self._depart_indices = self._reloading_virtual_depos_indices[1::2]
        self._num_of_nodes = len(self._matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)
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
        depot_ids_start = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)
        # TODO depot_ids_end = self._graph_exporter.export_basis_nodes_indices(self._match_input.graph)
        manager = pywrapcp.RoutingIndexManager(self._num_of_nodes,
                                               self._matcher_input.empty_board.amount_of_formations(),
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
                                                        self._arrive_indices, self._depart_indices)
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
            start_index = self._routing_model.Start(edd_index)
            graph_start_index = self._index_manager.IndexToNode(start_index)
            start_drone_loading_dock = self._create_start_drone_loading_dock(graph_start_index, start_index, solution)
            index = solution.Value(self._routing_model.NextVar(start_index))
            matched_requests = []
            while not self._routing_model.IsEnd(index) and not self._routing_model.IsStart(index):
                graph_index = self._index_manager.IndexToNode(index)
                if graph_index in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
                    matched_requests.append(
                        self._create_matched_delivery_request(graph_index, index, solution))
                elif graph_index in self._arrive_indices:
                    graph_index = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)[0]
                    end_drone_loading_dock = self._create_end_drone_loading_dock(graph_index, index, solution)
                    drone_deliveries.append(
                        self._create_drone_delivery(edd_index, start_drone_loading_dock, end_drone_loading_dock,
                                                    matched_requests))
                    matched_requests = []
                elif graph_index in self._depart_indices:
                    graph_index = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)[0]
                    start_drone_loading_dock = self._create_start_drone_loading_dock(
                        graph_index, index, solution)
                index = solution.Value(self._routing_model.NextVar(index))
            if self._routing_model.IsEnd(index):
                graph_index = self._index_manager.IndexToNode(index)
                end_drone_loading_dock = self._create_end_drone_loading_dock(graph_index, index, solution)
                drone_deliveries.append(
                    self._create_drone_delivery(edd_index, start_drone_loading_dock, end_drone_loading_dock,
                                                matched_requests))
        return drone_deliveries

    def _extract_unmatched_delivery_requests(self, solution: Assignment) -> List[UnmatchedDeliveryRequest]:
        if solution is None:
            return []
        unmatched_delivery_request = []
        for index in range(self._num_of_nodes):
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

    def _create_start_drone_loading_dock(self, graph_index: int, index: int,
                                   solution: Assignment) -> MatchedDroneLoadingDock:
        if solution is None:
            raise ValueError('No Solution!')

        delivery_time_window = self._get_start_dock_time_window(graph_index, index, solution)
        return MatchedDroneLoadingDock(
            graph_index=graph_index,
            drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                self.matcher_input.graph, graph_index),
            delivery_time_window=delivery_time_window)

    def _create_end_drone_loading_dock(self, graph_index: int, index: int,
                                   solution: Assignment) -> MatchedDroneLoadingDock:
        if solution is None:
            raise ValueError('No Solution!')

        delivery_time_window = self._get_delivery_time_window(index, solution)
        return MatchedDroneLoadingDock(
            graph_index=graph_index,
            drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                self.matcher_input.graph, graph_index),
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

    def _get_start_dock_time_window(self, graph_index, index, solution):
        first_delivery_index = solution.Value(self._routing_model.NextVar(index))
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        first_delivery_min_arrival_time = solution.Min(travel_time_dimension.CumulVar(first_delivery_index))
        travel_time_from_dock_to_first_delivery_in_min = self._graph_exporter.export_travel_times(
            self._matcher_input.graph)[graph_index][self._index_manager.IndexToNode(first_delivery_index)]
        service_time_in_min = float(first_delivery_min_arrival_time
                                    - travel_time_from_dock_to_first_delivery_in_min)
        return TimeWindowExtension(
            since=self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=service_time_in_min))),
            until=self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=service_time_in_min))))
