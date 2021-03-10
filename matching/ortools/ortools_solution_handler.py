from datetime import timedelta
from typing import List

from ortools.constraint_solver.pywrapcp import Assignment, RoutingIndexManager, RoutingModel

from common.entities.base_entities.drone_delivery import DroneDelivery, MatchedDeliveryRequest, MatchedDroneLoadingDock
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.temporal import TimeWindowExtension, TimeDeltaExtension
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher_constraints import OrToolsDimensionDescription


class ORToolsSolutionHandler:
    def __init__(self, graph_exporter: OrtoolsGraphExporter, index_manager: RoutingIndexManager,
                 routing_model: RoutingModel, matcher_input: MatcherInput):

        self._graph_exporter = graph_exporter
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input

    def create_drone_delivery_board(self, solution: Assignment) -> DroneDeliveryBoard:

        return DroneDeliveryBoard(drone_deliveries=self._create_drone_deliveries(solution),
                                  unmatched_delivery_requests=self._extract_unmatched_delivery_requests(solution))

    def _create_drone_deliveries(self, solution: Assignment) -> List[DroneDelivery]:
        drone_deliveries = []
        for edd_index, empty_drone_delivery in enumerate(self._matcher_input.empty_board.empty_drone_deliveries):
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
                        self._matcher_input.graph, graph_index)))

        return unmatched_delivery_request

    def _create_matched_delivery_requests(self, edd_index: int, solution: Assignment) -> List[MatchedDeliveryRequest]:
        matched_requests = []

        start_index = self._routing_model.Start(edd_index)
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
        return DroneDelivery(self._matcher_input.empty_board.empty_drone_deliveries[edd_index].id,
                             self._matcher_input.empty_board.empty_drone_deliveries[
                                 edd_index].drone_formation,
                             matched_requests, start_drone_loading_dock, end_drone_loading_dock)

    def _create_matched_delivery_request(self, graph_index: int, index: int,
                                         solution: Assignment) -> MatchedDeliveryRequest:
        return MatchedDeliveryRequest(
            graph_index=graph_index,
            delivery_request=self._graph_exporter.get_delivery_request(
                self._matcher_input.graph,
                graph_index),
            matched_delivery_option_index=0,
            delivery_time_window=self._get_delivery_time_window(index, solution))

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
                self._matcher_input.graph, graph_index),
            delivery_time_window=self._get_delivery_time_window(index, solution))

    def _get_delivery_time_window(self, index: int, solution: Assignment) -> TimeWindowExtension:
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        travel_time_var = travel_time_dimension.CumulVar(index)

        return TimeWindowExtension(
            since=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Min(travel_time_var))))),
            until=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Max(travel_time_var))))))
