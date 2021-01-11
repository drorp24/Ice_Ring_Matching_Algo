from datetime import timedelta
from typing import List

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel, Assignment

from common.entities.base_entities.drone_delivery import DroneDelivery, MatchedDroneLoadingDock, MatchedDeliveryRequest
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import Matcher
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher_constraints import ORToolsMatcherConstraints
from matching.ortools.ortools_matcher_objective import ORToolsMatcherObjective
from matching.ortools.ortools_matcher_search_params import ORToolsMatcherSearchParams


class ORToolsMatcher(Matcher):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)

        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = self._set_index_manager()
        self._routing_model = self._set_routing_model()
        self._search_parameters = ORToolsMatcherSearchParams(self.matcher_input).params

        self._set_objective()
        self._set_constraints()

    def match(self) -> DroneDeliveryBoard:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        return self._create_drone_delivery_board(solution)

    def _set_index_manager(self) -> RoutingIndexManager:
        num_vehicles = self._matcher_input.empty_board.num_of_formations()
        depot_ids_start = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)
        # TODO depot_ids_end = self._graph_exporter.export_basis_nodes_indices(self._match_input.graph)

        manager = pywrapcp.RoutingIndexManager(len(self.matcher_input.graph.nodes),
                                               num_vehicles,
                                               depot_ids_start[0])
        # TODO add depot_ids_end as forth param)

        return manager

    def _set_routing_model(self) -> RoutingModel:
        return pywrapcp.RoutingModel(self._index_manager)

    def _set_objective(self):
        ORToolsMatcherObjective(self._index_manager, self._routing_model, self.matcher_input).add_priority()

    def _set_constraints(self):
        matcher_constraints = ORToolsMatcherConstraints(self._index_manager, self._routing_model, self.matcher_input)
        matcher_constraints.add_demand()
        matcher_constraints.add_time()
        matcher_constraints.add_unmatched_penalty()

    def _create_drone_delivery_board(self, solution: Assignment) -> DroneDeliveryBoard:

        return DroneDeliveryBoard(drone_deliveries=self._create_drone_deliveries(solution),
                                  unmatched_delivery_requests=self._extract_unmatched_delivery_requests(solution))

    def _create_drone_deliveries(self, solution: Assignment) -> List[DroneDelivery]:
        drone_deliveries = []
        for edd_index, empty_drone_delivery in enumerate(self.matcher_input.empty_board.empty_drone_deliveries):
            start_drone_loading_dock = self._create_start_drone_loading_dock(edd_index, solution)
            matched_requests = self._create_matched_delivery_requests(edd_index, solution)
            end_drone_loading_dock = self._create_end_drone_loading_dock(edd_index, solution)
            drone_deliveries.append(
                self._create_drone_delivery(edd_index, start_drone_loading_dock, end_drone_loading_dock,
                                            matched_requests))
        return drone_deliveries

    def _extract_unmatched_delivery_requests(self, solution: Assignment) -> List[UnmatchedDeliveryRequest]:
        unmatched_delivery_request = []

        for index in range(self._routing_model.Size()):
            if self._routing_model.IsStart(index) or self._routing_model.IsEnd(index):
                continue
            if solution.Value(self._routing_model.NextVar(index)) == index:
                graph_index = self._index_manager.IndexToNode(index)
                unmatched_delivery_request.append(UnmatchedDeliveryRequest(
                    graph_index=graph_index,
                    delivery_request=self._graph_exporter.get_delivery_request(
                        self.matcher_input.graph, graph_index)))

        return unmatched_delivery_request

    def _create_matched_delivery_requests(self, edd_index: int, solution: Assignment) -> List[MatchedDeliveryRequest]:
        matched_requests = []

        start_index = self._routing_model.Start(edd_index)
        graph_start_index = self._index_manager.IndexToNode(start_index)
        index = solution.Value(self._routing_model.NextVar(start_index))
        while not self._routing_model.IsEnd(index) and not self._routing_model.IsStart(index):
            graph_index = self._index_manager.IndexToNode(index)
            if graph_index in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
                matched_requests.append(
                    self._create_matched_delivery_request(graph_index, index, solution))
                index = solution.Value(self._routing_model.NextVar(index))
        return matched_requests

    def _create_drone_delivery(self, edd_index: int, start_drone_loading_dock: MatchedDroneLoadingDock,
                               end_drone_loading_dock: MatchedDroneLoadingDock,
                               matched_requests: List[MatchedDeliveryRequest]) -> DroneDelivery:
        return DroneDelivery(self.matcher_input.empty_board.empty_drone_deliveries[edd_index].id,
                             self.matcher_input.empty_board.empty_drone_deliveries[
                                 edd_index].drone_formation,
                             matched_requests, start_drone_loading_dock, end_drone_loading_dock)

    def _create_matched_delivery_request(self, graph_index: int, index: int,
                                         solution: Assignment) -> MatchedDeliveryRequest:
        return MatchedDeliveryRequest(
            graph_index=graph_index,
            delivery_request=self._graph_exporter.get_delivery_request(
                self.matcher_input.graph,
                graph_index),
            matched_delivery_option_index=0,
            delivery_min_time=(self._get_min_time(index, solution)), delivery_max_time=(
                self._get_max_time(index, solution)))

    def _create_start_drone_loading_dock(self, edd_index: int, solution: Assignment) -> MatchedDroneLoadingDock:
        start_index = self._routing_model.Start(edd_index)
        graph_start_index = self._index_manager.IndexToNode(start_index)
        return self._create_drone_loading_dock(graph_start_index, start_index, solution)

    def _create_end_drone_loading_dock(self, edd_index: int, solution: Assignment) -> MatchedDroneLoadingDock:
        end_index = self._routing_model.End(edd_index)
        graph_end_index = self._index_manager.IndexToNode(end_index)
        return self._create_drone_loading_dock(graph_end_index, end_index, solution)

    def _create_drone_loading_dock(self, graph_index: int, index: int,
                                   solution: Assignment) -> MatchedDroneLoadingDock:
        return MatchedDroneLoadingDock(
            graph_index=graph_index,
            drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                self.matcher_input.graph, graph_index),
            delivery_min_time=(self._get_min_time(index, solution)),
            delivery_max_time=(self._get_max_time(index, solution)))

    def _get_min_time(self, index: int, solution: Assignment) -> DateTimeExtension:
        time_dimension = self._routing_model.GetDimensionOrDie('Time')
        time_var = time_dimension.CumulVar(index)
        return self._matcher_input.config.zero_time.add_time_delta(
            TimeDeltaExtension(timedelta(minutes=solution.Min(time_var))))

    def _get_max_time(self, index: int, solution: Assignment) -> DateTimeExtension:
        time_dimension = self._routing_model.GetDimensionOrDie('Time')
        time_var = time_dimension.CumulVar(index)
        return self._matcher_input.config.zero_time.add_time_delta(
            TimeDeltaExtension(timedelta(minutes=solution.Max(time_var))))
