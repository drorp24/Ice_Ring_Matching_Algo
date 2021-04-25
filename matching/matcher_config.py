from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.temporal import DateTimeExtension
from matching.constraint_config import ConstraintsConfig
from matching.monitor_config import MonitorConfig
from matching.solver_config import SolverConfig
from matching.solver_factory import create_solver_config


class MatcherConfig(JsonableBaseEntity):
    def __init__(self, zero_time: DateTimeExtension, solver: SolverConfig, constraints: ConstraintsConfig,
                 unmatched_penalty: int, reload_per_vehicle: int, monitor: MonitorConfig,
                 submatch_time_window_minutes: int):
        self._zero_time = zero_time
        self._solver = solver
        self._constraints = constraints
        self._unmatched_penalty = unmatched_penalty
        self._reload_per_vehicle = reload_per_vehicle
        self._monitor = monitor
        self._submatch_time_window_minutes = submatch_time_window_minutes

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

    @property
    def reload_per_vehicle(self) -> int:
        return self._reload_per_vehicle

    @property
    def monitor(self) -> MonitorConfig:
        return self._monitor

    @property
    def submatch_time_window_minutes(self) -> int:
        return self._submatch_time_window_minutes

    def __eq__(self, other):
        return all([self.zero_time == other.zero_time,
                    self.solver == other.solver,
                    self.unmatched_penalty == other.unmatched_penalty,
                    self.constraints == other.constraints,
                    self.reload_per_vehicle == other.reload_per_vehicle,
                    self.monitor == other.monitor,
                    self.submatch_time_window_minutes == other.submatch_time_window_minutes])

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return MatcherConfig(
            zero_time=DateTimeExtension.from_dict(dict_input["zero_time"]),
            solver=create_solver_config(dict_input["solver"]),
            constraints=ConstraintsConfig.dict_to_obj(dict_input["constraints"]),
            unmatched_penalty=dict_input["unmatched_penalty"],
            reload_per_vehicle=dict_input["reload_per_vehicle"],
            monitor=MonitorConfig.dict_to_obj(dict_input["monitor"]),
            submatch_time_window_minutes=dict_input["submatch_time_window_minutes"])
