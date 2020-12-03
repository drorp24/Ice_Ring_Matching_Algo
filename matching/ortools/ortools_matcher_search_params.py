from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from matching.matcher import MatchInput
from matching.ortools.ortools_strategy_factory import ORToolsStrategyFactory


class ORToolsMatcherSearchParams:
    def __init__(self,match_input: MatchInput):

        self._search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self._search_parameters.first_solution_strategy = ORToolsStrategyFactory.create_first_solution_strategy(
            match_input.config.first_solution_strategy)
        self._search_parameters.local_search_metaheuristic = ORToolsStrategyFactory.create_local_search_solver(
            match_input.config.solver.name)

        self._search_parameters.time_limit.seconds = match_input.config.solver.timeout_sec

    @property
    def get(self) -> RoutingSearchParameters:
        return self._search_parameters

