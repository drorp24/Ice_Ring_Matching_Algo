from dataclasses import dataclass

from common.entities.base_entity import JsonableBaseEntity
from common.entities.temporal import DateTimeExtension


class MatchSolver(JsonableBaseEntity):
    def __init__(self, full_name: str, timeout_sec: int):
        # When using metaheuristics, need to set a time limit for the solver—otherwise the solver will not terminate.
        self._name = str.upper(full_name.partition(':')[2]) if str.upper(
            full_name.partition(':')[2]) != "" else str.upper(full_name.partition(':')[0])
        self._timeout_sec = timeout_sec if timeout_sec != 0 else 30

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return MatchSolver(
            full_name=dict_input["name"],
            timeout_sec=dict_input["timeout_sec"])

    @property
    def timeout_sec(self) -> int:
        return self._timeout_sec

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, other):
        return (self.timeout_sec == other.timeout_sec) and \
               (self.name == other.name)


class CapacityConstraints(JsonableBaseEntity):
    def __init__(self, count_capacity_from_zero):
        self._count_capacity_from_zero = count_capacity_from_zero

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return CapacityConstraints(
            count_capacity_from_zero=dict_input["count_capacity_from_zero"])

    @property
    def count_capacity_from_zero(self) -> bool:
        return self._count_capacity_from_zero

    def __eq__(self, other):
        return self.count_capacity_from_zero == other.count_capacity_from_zero


class TimeConstraints(JsonableBaseEntity):
    def __init__(self, waiting_time_allowed_min: int, max_total_drone_time_min: int, count_time_from_zero: bool):
        self._waiting_time_allowed_min = waiting_time_allowed_min
        self._max_total_drone_time_min = max_total_drone_time_min
        self._count_time_from_zero = count_time_from_zero

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return TimeConstraints(
            waiting_time_allowed_min=dict_input["waiting_time_allowed_min"],
            max_total_drone_time_min=dict_input["max_total_drone_time_min"],
            count_time_from_zero=dict_input["count_time_from_zero"])

    @property
    def waiting_time_allowed_min(self):
        return self._waiting_time_allowed_min

    @property
    def max_total_drone_time_min(self):
        return self._max_total_drone_time_min

    @property
    def count_time_from_zero(self):
        return self._count_time_from_zero

    def __eq__(self, other):
        return (self.waiting_time_allowed_min == other.waiting_time_allowed_min) and \
               (self.max_total_drone_time_min == other.max_total_drone_time_min) and \
               (self.count_time_from_zero == other.count_time_from_zero)


class PriorityConstraints(JsonableBaseEntity):
    def __init__(self, count_priority_from_zero: bool):
        self._count_priority_from_zero = count_priority_from_zero

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return PriorityConstraints(
            count_priority_from_zero=dict_input["count_priority_from_zero"])

    @property
    def count_priority_from_zero(self) -> True:
        return self._count_priority_from_zero

    def __eq__(self, other):
        return self.count_priority_from_zero == other.count_priority_from_zero


class MatchConstraints(JsonableBaseEntity):
    def __init__(self, capacity_constraints: CapacityConstraints, time_constraints: TimeConstraints,
                 priority_constraints: PriorityConstraints):
        self._capacity_constraints = capacity_constraints
        self._time_constraints = time_constraints
        self._priority_constraints = priority_constraints

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return MatchConstraints(
            capacity_constraints=CapacityConstraints.dict_to_obj(dict_input["capacity"]),
            time_constraints=TimeConstraints.dict_to_obj(dict_input["time"]),
            priority_constraints=PriorityConstraints.dict_to_obj(dict_input["priority"]))

    @property
    def capacity(self) -> CapacityConstraints:
        return self._capacity_constraints

    @property
    def time(self) -> TimeConstraints:
        return self._time_constraints

    @property
    def priority(self) -> PriorityConstraints:
        return self._priority_constraints

    def __eq__(self, other):
        return (self.capacity == other.capacity) and \
               (self.time == other.time) and \
               (self.priority == other.priority)


@dataclass
class MatchConfigProperties:
    zero_time: DateTimeExtension
    first_solution_strategy: str
    solver: MatchSolver
    match_constraints: MatchConstraints
    dropped_penalty: int


class MatchConfig(JsonableBaseEntity):
    def __init__(self, match_config_properties: MatchConfigProperties):
        self._match_config_properties = match_config_properties

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        match_config_properties = MatchConfigProperties(
            zero_time=DateTimeExtension.from_dict(dict_input["zero_time"]),
            first_solution_strategy=dict_input["first_solution_strategy"],
            solver=MatchSolver.dict_to_obj(dict_input["solver"]),
            match_constraints=MatchConstraints.dict_to_obj(dict_input["constraints"]),
            dropped_penalty=dict_input["dropped_penalty"])

        return MatchConfig(match_config_properties)

    @property
    def zero_time(self) -> DateTimeExtension:
        return self._match_config_properties.zero_time

    @property
    def first_solution_strategy(self) -> str:
        return self._match_config_properties.first_solution_strategy

    @property
    def solver(self) -> MatchSolver:
        return self._match_config_properties.solver

    @property
    def dropped_penalty(self) -> int:
        return self._match_config_properties.dropped_penalty

    @property
    def constraints(self) -> MatchConstraints:
        return self._match_config_properties.match_constraints

    def __eq__(self, other):
        return (self.zero_time == other.zero_time) and \
               (self.first_solution_strategy == other.first_solution_strategy) and \
               (self.solver == other.solver) and \
               (self.dropped_penalty == other.dropped_penalty) and \
               (self.constraints == other.constraints)
