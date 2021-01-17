from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.temporal import DateTimeExtension
from matching.constraint_config import ConstraintsConfig
from matching.solver_config import SolverConfig
from matching.solver_factory import create_solver_config


class MatcherConfig(JsonableBaseEntity):
    def __init__(self, zero_time: DateTimeExtension, solver: SolverConfig, constraints: ConstraintsConfig,
                 unmatched_penalty: int):
        self._zero_time = zero_time
        self._solver = solver
        self._constraints = constraints
        self._unmatched_penalty = unmatched_penalty

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return MatcherConfig(
            zero_time=DateTimeExtension.from_dict(dict_input["zero_time"]),
            solver=create_solver_config(dict_input["solver"]),
            constraints=ConstraintsConfig.dict_to_obj(dict_input["constraints"]),
            unmatched_penalty=dict_input["unmatched_penalty"])

    @property
    def zero_time(self) -> DateTimeExtension:
        return self._zero_time

    @property
    def solver(self) -> SolverConfig:
        return self._solver

    @property
    def constraints(self) -> ConstraintsConfig:
        return self._constraints

    @property
    def unmatched_penalty(self) -> int:
        return self._unmatched_penalty

    def __eq__(self, other):
        return (self.zero_time == other.zero_time) and \
               (self.solver == other.solver) and \
               (self.unmatched_penalty == other.unmatched_penalty) and \
               (self.constraints == other.constraints)
