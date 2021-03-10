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
                 routing_model: RoutingModel, matcher_input: MatcherInput, reloading_depos_arrive_indices: [int],
                 reloading_depos_depart_indices: [int]):

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

    def create_drone_delivery_board(self, solution: Assignment) -> DroneDeliveryBoard:

        return DroneDeliveryBoard(drone_deliveries=self._create_drone_deliveries(solution),
                                  unmatched_delivery_requests=self._extract_unmatched_delivery_requests(solution))

    def _create_drone_deliveries(self, solution: Assignment) -> List[DroneDelivery]:
        if solution is None:
            return []
        drone_deliveries = []
        for edd_index, empty_drone_delivery in enumerate(self._matcher_input.empty_board.empty_drone_deliveries):
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
                        self._matcher_input.graph, graph_index)))

        return unmatched_delivery_request

    def _create_drone_delivery(self, edd_index: int, start_drone_loading_dock: MatchedDroneLoadingDock,
                               end_drone_loading_dock: MatchedDroneLoadingDock,
                               matched_requests: List[MatchedDeliveryRequest]) -> DroneDelivery:
        return DroneDelivery(self._matcher_input.empty_board.empty_drone_deliveries[edd_index].id,
                             self._matcher_input.empty_board.empty_drone_deliveries[
                                 edd_index].drone_formation,
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

    def _create_start_drone_loading_dock(self, graph_index: int, index: int,
                                   solution: Assignment) -> MatchedDroneLoadingDock:
        if solution is None:
            raise ValueError('No Solution!')

        delivery_time_window = self._get_start_dock_time_window(graph_index, index, solution)
        return MatchedDroneLoadingDock(
            graph_index=graph_index,
            drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                self._matcher_input.graph, graph_index),
            delivery_time_window=delivery_time_window)

    def _create_end_drone_loading_dock(self, graph_index: int, index: int,
                                   solution: Assignment) -> MatchedDroneLoadingDock:
        if solution is None:
            raise ValueError('No Solution!')

        delivery_time_window = self._get_delivery_time_window(index, solution)
        return MatchedDroneLoadingDock(
            graph_index=graph_index,
            drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                self._matcher_input.graph, graph_index),
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

    def _set_reloading_depos_for_each_formation(self, num_of_reloading_depo_nodes_per_formation):
        for formation_index in range(self._matcher_input.empty_board.amount_of_formations()):
            formation_reloading_depos = self._reloading_virtual_depos_indices[
                                        formation_index * num_of_reloading_depo_nodes_per_formation:
                                        (formation_index + 1) * num_of_reloading_depo_nodes_per_formation]
            for node in [formation_reloading_depos[0]]:
                index = self._index_manager.NodeToIndex(node)
                must_have_not_active_option_index = -1
                self._routing_model.VehicleVar(index).SetValues([must_have_not_active_option_index, formation_index])
