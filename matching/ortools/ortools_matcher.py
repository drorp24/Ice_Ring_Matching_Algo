from datetime import timedelta
from typing import List

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel, Assignment

from common.entities.drone_delivery import MatchedDeliveryRequest, DroneDelivery, MatchedDroneLoadingDock
from common.entities.drone_delivery_board import DroneDeliveryBoard, DroppedDeliveryRequest
from common.entities.temporal import TimeDeltaExtension
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
        self._manager = self._set_manager()
        self._routing = self._set_routing()
        self._search_parameters = ORToolsMatcherSearchParams(self.matcher_input).params

        self._set_objective()
        self._set_constraints()

    def _set_manager(self) -> RoutingIndexManager:
        #travel_times_matrix = self._graph_exporter.export_travel_times(self._matcher_input.graph)
        num_vehicles = self._matcher_input.empty_board.num_of_formations()
        depot_ids_start = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)
        # TODO depot_ids_end = self._graph_exporter.export_basis_nodes_indices(self._match_input.graph)

        manager = pywrapcp.RoutingIndexManager(len(self.matcher_input.graph.nodes),
                                               num_vehicles,
                                               depot_ids_start[0])
        # TODO add depot_ids_end as forth param)

        return manager

    def _set_routing(self) -> RoutingModel:
        return pywrapcp.RoutingModel(self._manager)

    def _set_objective(self):
        ORToolsMatcherObjective(self._graph_exporter, self._manager, self._routing, self.matcher_input).add_priority()

    def _set_constraints(self):
        matcher_constraints = ORToolsMatcherConstraints(self._graph_exporter, self._manager, self._routing,
                                                        self.matcher_input)

        matcher_constraints.add_demand()
        matcher_constraints.add_time()
        matcher_constraints.add_dropped_penalty()

    def match(self) -> DroneDeliveryBoard:
        solution = self._routing.SolveWithParameters(self._search_parameters)
        return self._create_drone_delivery_board(solution)

    def _create_drone_delivery_board(self, solution: Assignment) -> DroneDeliveryBoard:

        return DroneDeliveryBoard(drone_deliveries=self._create_drone_deliveries(solution),
                                  dropped_delivery_requests=self._extract_dropped(solution))

    def _extract_dropped(self, solution: Assignment) -> List[DroppedDeliveryRequest]:
        dropped_delivery_request = []

        for index in range(self._routing.Size()):
            if self._routing.IsStart(index) or self._routing.IsEnd(index):
                continue
            if solution.Value(self._routing.NextVar(index)) == index:
                graph_index = self._manager.IndexToNode(index)
                dropped_delivery_request.append(DroppedDeliveryRequest(graph_index=graph_index,
                                                       delivery_request=self._graph_exporter.get_delivery_request(
                                                           self.matcher_input.graph, graph_index)))

        return dropped_delivery_request

    # TODO: split function to small funct
    def _create_drone_deliveries(self, solution: Assignment):
        drone_deliveries = []

        for edd_index, empty_drone_delivery in enumerate(self.matcher_input.empty_board.empty_drone_deliveries):
            matched_requests = []

            index = self._routing.Start(edd_index)
            graph_index = self._manager.IndexToNode(index)

            start_drone_loading_docks = MatchedDroneLoadingDock(
                graph_index=graph_index,
                drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                    self.matcher_input.graph, graph_index),
                delivery_min_time=(self._get_min_time(solution, index)),
                delivery_max_time=(self._get_max_time(solution, index)))

            index = solution.Value(self._routing.NextVar(index))
            while not self._routing.IsEnd(index) and not self._routing.IsStart(index):

                graph_index = self._manager.IndexToNode(index)

                if graph_index in self._graph_exporter.export_delivery_request_nodes_indices(self._matcher_input.graph):
                    matched_requests.append(
                        MatchedDeliveryRequest(
                            graph_index=graph_index,
                            delivery_request=self._graph_exporter.get_delivery_request(
                                self.matcher_input.graph,
                                graph_index),
                            matched_delivery_option_index=0,
                            delivery_min_time=(self._get_min_time(solution,
                                                                  index)), delivery_max_time=(
                                self._get_max_time(solution, index))))

                    index = solution.Value(self._routing.NextVar(index))

            graph_index = self._manager.IndexToNode(index)
            end_drone_loading_docks = MatchedDroneLoadingDock(
                graph_index=graph_index,
                drone_loading_dock=self._graph_exporter.get_drone_loading_dock(
                    self.matcher_input.graph, graph_index),
                delivery_min_time=(self._get_min_time(solution, index)),
                delivery_max_time=(
                    self._get_max_time(solution, index)))

            drone_deliveries.append(
                DroneDelivery(self.matcher_input.empty_board.empty_drone_deliveries[edd_index].id,
                              self.matcher_input.empty_board.empty_drone_deliveries[
                                  edd_index].drone_formation,
                              matched_requests, start_drone_loading_docks, end_drone_loading_docks))

        return drone_deliveries

    def _get_min_time(self, solution, index):
        time_dimension = self._routing.GetDimensionOrDie('Time')
        time_var = time_dimension.CumulVar(index)
        return self._matcher_input.config.zero_time.add_time_delta(
            TimeDeltaExtension(timedelta(minutes=solution.Min(time_var))))

    def _get_max_time(self, solution, index):
        time_dimension = self._routing.GetDimensionOrDie('Time')
        time_var = time_dimension.CumulVar(index)
        return self._matcher_input.config.zero_time.add_time_delta(
            TimeDeltaExtension(timedelta(minutes=solution.Max(time_var))))
