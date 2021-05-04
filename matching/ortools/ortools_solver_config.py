from ortools.constraint_solver.routing_enums_pb2 import LocalSearchMetaheuristic, FirstSolutionStrategy

from common.entities.base_entities.base_entity import JsonableBaseEntity
from matching.solver_config import SolverConfig, SolverVendor

DEFAULT_TIMEOUT_FOR_META_HEURISTICS = 30


class ORToolsSolverConfig(SolverConfig, JsonableBaseEntity):

    # The first solution strategies include:
    # ['UNSET', 'AUTOMATIC', 'PATH_CHEAPEST_ARC', 'PATH_MOST_CONSTRAINED_ARC', 'EVALUATOR_STRATEGY', 'SAVINGS', 'SWEEP',
    # 'CHRISTOFIDES', 'ALL_UNPERFORMED', 'BEST_INSERTION', 'PARALLEL_CHEAPEST_INSERTION',
    # 'SEQUENTIAL_CHEAPEST_INSERTION', 'LOCAL_CHEAPEST_INSERTION', 'GLOBAL_CHEAPEST_ARC',
    # 'LOCAL_CHEAPEST_ARC', 'FIRST_UNBOUND_MIN_VALUE']",

    # The Local Search Strategies include:
    # ['UNSET', 'AUTOMATIC', 'GREEDY_DESCENT', 'GUIDED_LOCAL_SEARCH', 'SIMULATED_ANNEALING', 'TABU_SEARCH',
    # 'GENERIC_TABU_SEARCH']

    def __init__(self, first_solution_strategy: str, local_search_strategy: str, timeout_sec: int):
        super().__init__(SolverVendor.OR_TOOLS, first_solution_strategy, local_search_strategy,
                         self.validate_timeout_sec(timeout_sec))

    def get_first_solution_strategy_as_int(self) -> int:
        return FirstSolutionStrategy.DESCRIPTOR.enum_values_by_name.get(
            str.upper(self.first_solution_strategy)).number

    def get_local_search_strategy_as_int(self) -> int:
        return LocalSearchMetaheuristic.DESCRIPTOR.enum_values_by_name.get(
            str.upper(self.local_search_strategy)).number

    def validate_timeout_sec(self, timeout_sec: int) -> int:
        # When using metaheuristics, need to set a time limit for the solver—otherwise the solver will not terminate.
        return DEFAULT_TIMEOUT_FOR_META_HEURISTICS if \
            timeout_sec == 0 and self.is_meta_heuristic() else timeout_sec

    def is_meta_heuristic(self) -> bool:
        if self.get_local_search_strategy_as_int() in [LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
                                                       LocalSearchMetaheuristic.SIMULATED_ANNEALING,
                                                       LocalSearchMetaheuristic.TABU_SEARCH,
                                                       LocalSearchMetaheuristic.GENERIC_TABU_SEARCH
                                                       ]:
            return True

        return False

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        new_copy = ORToolsSolverConfig(self.first_solution_strategy,
                                       self.local_search_strategy, self.timeout_sec)
        memodict[id(self)] = new_copy
        return new_copy

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return ORToolsSolverConfig(
            first_solution_strategy=dict_input["first_solution_strategy"],
            local_search_strategy=dict_input["local_search_strategy"],
            timeout_sec=dict_input["timeout_sec"])
