from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import MatchInput, Matcher
from matching.matching_solution import MatchingSolution
from matching.ortools.ortools_matcher_constraints import ORToolsMatcherConstraints
from matching.ortools.ortools_matcher_objective import ORToolsMatcherObjective
from matching.ortools.ortools_matcher_search_params import ORToolsMatcherSearchParams
from matching.ortools.ortools_matching_solution import ORToolsMatchingSolution


class ORToolsMatcher(Matcher):

    def __init__(self, match_input: MatchInput):
        super().__init__(match_input)

        self._graph_exporter = OrtoolsGraphExporter()
        self._manager = self._set_manager()
        self._routing = self._set_routing()
        self._search_parameters = ORToolsMatcherSearchParams(self.match_input).get

        self._set_objective()
        self._set_constraints()

    @property
    def graph_exporter(self) -> OrtoolsGraphExporter:
        return self._graph_exporter

    @property
    def manager(self) -> RoutingIndexManager:
        return self._manager

    @property
    def routing(self) -> RoutingModel:
        return self._routing

    def _set_manager(self) -> RoutingIndexManager:
        travel_times_matrix = self._graph_exporter.export_travel_times(self._match_input.graph)
        num_vehicles = self._match_input.empty_board.num_of_formations
        depot_ids_start = self._graph_exporter.export_basis_nodes_idndices(self._match_input.graph)
        depot_ids_end = self._graph_exporter.export_basis_nodes_indices(self._match_input.graph)

        manager =  pywrapcp.RoutingIndexManager(len(travel_times_matrix),
                                            num_vehicles,
                                            depot_ids_start[0])
                                            #depot_ids_end)

        return manager

    def _set_routing(self) -> RoutingModel:
        return pywrapcp.RoutingModel(self._manager)

    def _set_objective(self):
        ORToolsMatcherObjective(self._graph_exporter, self._manager, self._routing, self.match_input).add_priority()

    def _set_constraints(self):
        matcher_constraints = ORToolsMatcherConstraints(self._graph_exporter, self._manager, self._routing,
                                                        self.match_input)

        matcher_constraints.add_demand()
        matcher_constraints.add_time()
        matcher_constraints.add_dropped_penalty()

    def match(self) -> MatchingSolution:
        solution = self._routing.SolveWithParameters(self._search_parameters)
        # TODO "delete monitor none"
        return ORToolsMatchingSolution(self, solution, None)
