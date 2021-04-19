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
from matching.ortools.ortools_solution_handler import ORToolsSolutionHandler

''' Reloading depo consists of 2 nodes:
arrive node & depart node so we can reset the cumulated travel_time between them.'''
NUM_OF_NODES_IN_RELOADING_DEPO = 2


class Reloader:
    def __init__(self, matcher_input: MatcherInput):
        self._matcher_input = matcher_input
        num_of_reloading_depo_nodes_per_formation = \
            self._matcher_input.config.reload_per_vehicle * NUM_OF_NODES_IN_RELOADING_DEPO
        num_of_reloading_depo_nodes = \
            self._matcher_input.delivering_drones_board.amount_of_formations() \
            * num_of_reloading_depo_nodes_per_formation
        self._reloading_virtual_depos_indices = list(range(
            len(self._matcher_input.graph.nodes),
            len(self._matcher_input.graph.nodes) + num_of_reloading_depo_nodes))
        self._arrive_indices = self._calc_reload_arriving_nodes()
        self._depart_indices = self._calc_reload_departing_nodes()
        self._num_of_nodes = len(self._matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)
        self._reloading_depots_per_vehicle = {
            vehicle_index: depots
            for (vehicle_index, depots)
            in enumerate([self._reloading_virtual_depos_indices[
                          formation_index * num_of_reloading_depo_nodes_per_formation:
                          (formation_index + 1) * num_of_reloading_depo_nodes_per_formation]
                          for formation_index in range(
                    self._matcher_input.delivering_drones_board.amount_of_formations())])}
        self._vehicle_per_reloading_depot = {}
        for vehicle_index in self._reloading_depots_per_vehicle.keys():
            for depo in self._reloading_depots_per_vehicle[vehicle_index]:
                self._vehicle_per_reloading_depot[depo] = vehicle_index

    @property
    def num_of_nodes(self):
        return self._num_of_nodes

    @property
    def reloading_virtual_depos_indices(self):
        return self._reloading_virtual_depos_indices

    @property
    def arrive_indices(self):
        return self._arrive_indices

    @property
    def depart_indices(self):
        return self._depart_indices

    def get_reloading_depot_vehicle(self, depot_index) -> [int]:
        return self._vehicle_per_reloading_depot[depot_index]

    def get_vehicle_reloading_depots(self, vehicle_index) -> [int]:
        return self._reloading_depots_per_vehicle[vehicle_index]

    def _calc_reload_arriving_nodes(self):
        starting_index = 0
        return self._reloading_virtual_depos_indices[starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]

    def _calc_reload_departing_nodes(self):
        starting_index = 1
        return self._reloading_virtual_depos_indices[starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]


class ORToolsMatcher(Matcher):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = self._set_index_manager()
        self._routing_model = self._set_routing_model()
        self._search_parameters = self._set_search_params()
        self._reloader = Reloader(matcher_input)
        self._start_depots_graph_indices_of_vehicles = self._get_start_depots_graph_indices_of_vehicles()
        self._end_depots_graph_indices_of_vehicles = self._get_end_depots_graph_indices_of_vehicles()
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
