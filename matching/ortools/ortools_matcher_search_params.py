from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.routing_enums_pb2 import _FIRSTSOLUTIONSTRATEGY_VALUE, _LOCALSEARCHMETAHEURISTIC_VALUE
from ortools.constraint_solver.routing_parameters_pb2 import RoutingSearchParameters

from matching.matcher import MatcherInput


class ORToolsMatcherSearchParams:
    def __init__(self, match_input: MatcherInput):
        self._search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        self._search_parameters.first_solution_strategy = _FIRSTSOLUTIONSTRATEGY_VALUE.values_by_name.get(
            str.upper(match_input.config.first_solution_strategy.partition(':')[2])).number

        self._search_parameters.local_search_metaheuristic = _LOCALSEARCHMETAHEURISTIC_VALUE.values_by_name.get(
            match_input.config.solver.name).number

        self._search_parameters.time_limit.seconds = match_input.config.solver.timeout_sec

    @property
    def params(self) -> RoutingSearchParameters:
        return self._search_parameters
