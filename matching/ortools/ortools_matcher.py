from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingModel
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.initial_solution import Routes
from matching.matcher import Matcher
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_index_manager_wrapper import OrToolsIndexManagerWrapper
from matching.ortools.ortools_matcher_constraints import ORToolsMatcherConstraints
from matching.ortools.ortools_matcher_monitor import ORToolsMatcherMonitor
from matching.ortools.ortools_matcher_objective import ORToolsMatcherObjective
from matching.ortools.ortools_reloader import ORToolsReloader
from matching.ortools.ortools_solution_handler import ORToolsSolutionHandler


class ORToolsMatcher(Matcher):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)
        self._reloader = ORToolsReloader(matcher_input)
        self._graph_exporter = OrtoolsGraphExporter()
        self._start_depots_graph_indices_of_vehicles = self._get_start_depots_graph_indices_of_vehicles()
        self._end_depots_graph_indices_of_vehicles = self._get_end_depots_graph_indices_of_vehicles()
        self._index_manager = self._set_index_manager()
        self._routing_model = self._set_routing_model()
        self._search_parameters = self._set_search_params()
        self._solution_handler = ORToolsSolutionHandler(self._graph_exporter, self._index_manager, self._routing_model,
                                                        self._matcher_input, self._reloader,
                                                        self._start_depots_graph_indices_of_vehicles,
                                                        self._end_depots_graph_indices_of_vehicles)
        self._set_objective()
        self._set_constraints()
        self._set_monitor()
        self._set_reloading_depos_for_each_formation()

    def _get_start_depots_graph_indices_of_vehicles(self):
        start_depots = [delivering_drones.start_loading_dock
                        for delivering_drones in self._matcher_input.delivering_drones_board.delivering_drones_list]
        return [self._graph_exporter.get_node_graph_index(
            self._matcher_input.graph, start_depot)
            for start_depot in start_depots]

    def _get_end_depots_graph_indices_of_vehicles(self):
        end_depots = [delivering_drones.end_loading_dock
                      for delivering_drones in self._matcher_input.delivering_drones_board.delivering_drones_list]
        return [self._graph_exporter.get_node_graph_index(
            self._matcher_input.graph, end_depot)
            for end_depot in end_depots]

    def match(self) -> DroneDeliveryBoard:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        if self._matcher_input.config.monitor.enabled:
            self.matcher_monitor.handle_monitor_data()
        return self._solution_handler.create_drone_delivery_board(solution)

    def match_to_routes(self) -> Routes:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        return self._solution_handler.get_routes(solution=solution)

    def match_from_init_solution(self, initial_routes: Routes) -> DroneDeliveryBoard:
        self._routing_model.CloseModelWithParameters(self._search_parameters)
        initial_solution = self._routing_model.ReadAssignmentFromRoutes(initial_routes.as_list(), False)
        solution = self._routing_model.SolveFromAssignmentWithParameters(initial_solution, self._search_parameters)
        return self._solution_handler.create_drone_delivery_board(solution)

    def _set_index_manager(self) -> OrToolsIndexManagerWrapper:
        manager = pywrapcp.RoutingIndexManager(self._reloader.num_of_nodes,
                                               self._matcher_input.delivering_drones_board.amount_of_formations(),
                                               self._start_depots_graph_indices_of_vehicles,
                                               self._end_depots_graph_indices_of_vehicles)
        return OrToolsIndexManagerWrapper(manager)

    def _set_routing_model(self) -> RoutingModel:
        return pywrapcp.RoutingModel(self._index_manager.get_internal())

    def _set_objective(self):
        objective = ORToolsMatcherObjective(self._index_manager, self._routing_model, self.matcher_input,
                                            self._reloader)
        objective.add_priority()

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
                                                        self._reloader)
        #  TODO: should be reload depos for every formation type (size and package)
        matcher_constraints.add_demand()
        matcher_constraints.add_travel_cost()
        matcher_constraints.add_travel_time()
        matcher_constraints.add_session_time()
        matcher_constraints.add_unmatched_penalty()

    def _set_monitor(self):
        if not self.matcher_input.config.monitor.enabled:
            return

        self.matcher_monitor = ORToolsMatcherMonitor(self._graph_exporter, self._index_manager, self._routing_model,
                                                     self._search_parameters, self.matcher_input,
                                                     self._solution_handler)
        self.matcher_monitor.add_search_monitor()

    def _set_reloading_depos_for_each_formation(self):
        for formation_index in range(self.matcher_input.delivering_drones_board.amount_of_formations()):
            for node in self._reloader.get_vehicle_reloading_depots(formation_index):
                index = self._index_manager.node_to_index(node)
                must_have_not_active_option_index = -1
                self._routing_model.VehicleVar(index).SetValues([must_have_not_active_option_index, formation_index])
