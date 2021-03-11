from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_delivery import DroneDelivery, MatchedDroneLoadingDock, MatchedDeliveryRequest
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.temporal import TimeDeltaExtension, TimeWindowExtension
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import Matcher
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher_constraints import ORToolsMatcherConstraints
from matching.ortools.ortools_matcher_objective import ORToolsMatcherObjective
from matching.ortools.ortools_solution_handler import ORToolsSolutionHandler


class ORToolsMatcher(Matcher):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)
        self._matcher_input = matcher_input
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = self._set_index_manager()
        self._routing_model = self._set_routing_model()
        self._search_parameters = self._set_search_params()
        self._solution_handler = ORToolsSolutionHandler(self._graph_exporter, self._index_manager, self._routing_model,
                                                        self._matcher_input)

        self._set_objective()
        self._set_constraints()

    def match(self) -> DroneDeliveryBoard:
        solution = self._routing_model.SolveWithParameters(self._search_parameters)
        if ORToolsMatcher.is_solution_valid(solution):
            return self._solution_handler.create_drone_delivery_board(solution)
        else:
            return DroneDeliveryBoard([], [UnmatchedDeliveryRequest(i, node.internal_node) for i, node in enumerate(self.matcher_input.graph.nodes) if
                                           isinstance(node.internal_node, DeliveryRequest)])

    @staticmethod
    def is_solution_valid(solution):
        return solution is not None

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
