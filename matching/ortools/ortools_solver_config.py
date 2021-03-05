from ortools.constraint_solver.routing_enums_pb2 import LocalSearchMetaheuristic, FirstSolutionStrategy

from common.entities.base_entities.base_entity import JsonableBaseEntity
from matching.solver_config import SolverConfig, SolverVendor

DEFAULT_TIMEOUT_FOR_META_HEURISTICS = 30


class ORToolsSolverConfig(SolverConfig, JsonableBaseEntity):
    def __init__(self, vendor: SolverVendor, first_solution_strategy: str, local_search_strategy: str,
                 timeout_sec: int):
        super().__init__(vendor, first_solution_strategy, local_search_strategy, timeout_sec)

        self._timeout_sec = self.validate_timeout_sec(timeout_sec)

    @property
    def first_solution_strategy(self) -> str:
        return super().first_solution_strategy

    @property
    def local_search_strategy(self) -> str:
        return super().local_search_strategy

    @property
    def vendor(self) -> SolverVendor:
        return super().vendor

    @property
    def timeout_sec(self) -> int:
        return super().timeout_sec

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

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return ORToolsSolverConfig(
            vendor=SolverVendor.dict_to_obj(dict_input["vendor"]),
            first_solution_strategy=dict_input["first_solution_strategy"],
            local_search_strategy=dict_input["local_search_strategy"],
            timeout_sec=dict_input["timeout_sec"])
