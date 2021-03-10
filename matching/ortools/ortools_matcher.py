from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import Matcher
from matching.matcher_input import MatcherInput
from matching.monitor_plotter import create_monitor_figure
from matching.ortools.ortools_matcher_constraints import ORToolsMatcherConstraints, OrToolsDimensionDescription
from matching.ortools.ortools_matcher_monitor import ORToolsMatcherMonitor
from matching.ortools.ortools_matcher_constraints import ORToolsMatcherConstraints
from matching.ortools.ortools_matcher_objective import ORToolsMatcherObjective
from matching.ortools.ortools_solution_handler import ORToolsSolutionHandler


class ORToolsMatcher(Matcher):
    solutions = []

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)

        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = self._set_index_manager()
        self._routing_model = self._set_routing_model()
        self._search_parameters = self._set_search_params()
        self._solution_handler = ORToolsSolutionHandler(self._graph_exporter, self._index_manager, self._routing_model,
                                                        self._matcher_input)

        self._set_objective()
        self._set_constraints()
        self._set_monitor()

    def match(self) -> DroneDeliveryBoard:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        self._save_monitor_data()
        return self._solution_handler.create_drone_delivery_board(solution)

    def _set_index_manager(self) -> RoutingIndexManager:
        num_vehicles = self._matcher_input.empty_board.amount_of_formations()
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

    def _set_search_params(self) -> RoutingSearchParameters:

        self._search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        self._search_parameters.first_solution_strategy = \
            self.matcher_input.config.solver.get_first_solution_strategy_as_int()

        self._search_parameters.local_search_metaheuristic = \
            self.matcher_input.config.solver.get_local_search_strategy_as_int()

        self._search_parameters.time_limit.seconds = self.matcher_input.config.solver.timeout_sec

        return self._search_parameters

    def _set_constraints(self):
        matcher_constraints = ORToolsMatcherConstraints(self._index_manager, self._routing_model, self.matcher_input)
        matcher_constraints.add_demand()
        matcher_constraints.add_travel_cost()
        matcher_constraints.add_travel_time()
        matcher_constraints.add_unmatched_penalty()

    def _set_monitor(self):
        if not self.matcher_input.config.monitor.enabled:
            return

        self.matcher_monitor = ORToolsMatcherMonitor(self._graph_exporter, self._index_manager, self._routing_model,
                                                     self._search_parameters, self.matcher_input,
                                                     self._solution_handler)
        self.matcher_monitor.add_search_monitor()

    def _save_monitor_data(self):
        print(f'total iteration: {self.matcher_monitor.monitor.num_of_iterations}')
        monitor_config = self.matcher_input.config.monitor
        if not monitor_config.enabled or not (monitor_config.save_data or monitor_config.plot_data):
            return

        create_monitor_figure(self.matcher_monitor.monitor, self.matcher_input)

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
                self.matcher_input.graph, graph_index),
            delivery_time_window=self._get_delivery_time_window(index, solution))

    def _get_delivery_time_window(self, index: int, solution: Assignment) -> TimeWindowExtension:
        travel_time_dimension = self._routing_model.GetDimensionOrDie(OrToolsDimensionDescription.travel_time.value)
        travel_time_var = travel_time_dimension.CumulVar(index)

        return TimeWindowExtension(
            since=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Min(travel_time_var))))),
            until=(self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(timedelta(minutes=solution.Max(travel_time_var))))))
