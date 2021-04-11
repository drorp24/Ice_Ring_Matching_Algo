from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingModel
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
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


class ORToolsMatcher(Matcher):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)
        self._matcher_input = matcher_input
        num_of_reloading_depo_nodes_per_formation = matcher_input.config.reload_per_vehicle \
                                                    * NUM_OF_NODES_IN_RELOADING_DEPO
        num_of_reloading_depo_nodes = self._matcher_input.empty_board.amount_of_formations() \
                                      * num_of_reloading_depo_nodes_per_formation
        self._reloading_virtual_depos_indices = list(range(
            len(self._matcher_input.graph.nodes),
            len(self._matcher_input.graph.nodes) + num_of_reloading_depo_nodes))
        self._arrive_indices = self._calc_reload_arriving_nodes()
        self._depart_indices = self._calc_reload_departing_nodes()
        self._num_of_nodes = len(self._matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = self._set_index_manager()
        self._routing_model = self._set_routing_model()
        self._search_parameters = self._set_search_params()
        self._solution_handler = ORToolsSolutionHandler(self._graph_exporter, self._index_manager, self._routing_model,
                                                        self._matcher_input, self._arrive_indices, self._depart_indices)
        self._set_objective()
        self._set_constraints()
        self._set_monitor()
        # self._set_reloading_depos_for_each_formation(num_of_reloading_depo_nodes_per_formation)

    def _calc_reload_arriving_nodes(self):
        starting_index = 0
        return self._reloading_virtual_depos_indices[starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]

    def _calc_reload_departing_nodes(self):
        starting_index = 1
        return self._reloading_virtual_depos_indices[starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]

    def match(self) -> DroneDeliveryBoard:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        if ORToolsMatcher.is_solution_valid(solution):
            if self._matcher_input.config.monitor.enabled:
                self.matcher_monitor.handle_monitor_data()
            return self._solution_handler.create_drone_delivery_board(solution)
        else:
            return DroneDeliveryBoard([], [UnmatchedDeliveryRequest(i, node.internal_node) for i, node in enumerate(self.matcher_input.graph.nodes) if
                                           isinstance(node.internal_node, DeliveryRequest)])

    @staticmethod
    def is_solution_valid(solution):
        return solution is not None

    def match_to_routes(self) -> Routes:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        return self._solution_handler.get_routes(solution=solution)

    def match_from_init_solution(self, initial_routes: Routes) -> DroneDeliveryBoard:
        self._routing_model.CloseModelWithParameters(self._search_parameters)
        initial_solution = self._routing_model.ReadAssignmentFromRoutes(initial_routes.as_list(), False)
        solution = self._routing_model.SolveFromAssignmentWithParameters(initial_solution, self._search_parameters)
        return self._solution_handler.create_drone_delivery_board(solution)

    def _set_index_manager(self) -> OrToolsIndexManagerWrapper:
        depot_ids_start = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)
        # TODO depot_ids_end = self._graph_exporter.export_basis_nodes_indices(self._match_input.graph)
        manager = pywrapcp.RoutingIndexManager(self._num_of_nodes,
                                               self._matcher_input.empty_board.amount_of_formations(),
                                               depot_ids_start[0])
        # TODO add depot_ids_end as forth param)

        return OrToolsIndexManagerWrapper(manager)

    def _set_routing_model(self) -> RoutingModel:
        return pywrapcp.RoutingModel(self._index_manager.get_internal())

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

    def _set_monitor(self):
        if not self.matcher_input.config.monitor.enabled:
            return

        self.matcher_monitor = ORToolsMatcherMonitor(self._graph_exporter, self._index_manager, self._routing_model,
                                                     self._search_parameters, self.matcher_input,
                                                     self._solution_handler)
        self.matcher_monitor.add_search_monitor()

    def _set_reloading_depos_for_each_formation(self, num_of_reloading_depo_nodes_per_formation):
        for formation_index in range(self._matcher_input.empty_board.amount_of_formations()):
            formation_reloading_depos = self._reloading_virtual_depos_indices[
                                        formation_index * num_of_reloading_depo_nodes_per_formation:
                                        (formation_index + 1) * num_of_reloading_depo_nodes_per_formation]
            for node in [formation_reloading_depos[0]]:
                index = self._index_manager.node_to_index(node)
                must_have_not_active_option_index = -1
                self._routing_model.VehicleVar(index).SetValues([must_have_not_active_option_index, formation_index])
