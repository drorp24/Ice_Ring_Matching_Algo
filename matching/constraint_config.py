from common.entities.base_entities.base_entity import JsonableBaseEntity


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


class TimeConstraints(JsonableBaseEntity):
    def __init__(self, max_waiting_time: int, max_route_time: int, count_time_from_zero: bool):
        self._max_waiting_time = max_waiting_time
        self._max_route_time = max_route_time
        self._count_time_from_zero = count_time_from_zero

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return TimeConstraints(
            max_waiting_time=dict_input["max_waiting_time"],
            max_route_time=dict_input["max_route_time"],
            count_time_from_zero=dict_input["count_time_from_zero"])

    @property
    def max_waiting_time(self):
        return self._max_waiting_time

    @property
    def max_route_time(self):
        return self._max_route_time

    @property
    def count_time_from_zero(self):
        return self._count_time_from_zero

    def __eq__(self, other):
        return (self.max_waiting_time == other.max_waiting_time) and \
               (self.max_route_time == other.max_route_time) and \
               (self.count_time_from_zero == other.count_time_from_zero)


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


class ConstraintsConfig(JsonableBaseEntity):
    def __init__(self, capacity_constraints: CapacityConstraints, time_constraints: TimeConstraints,
                 priority_constraints: PriorityConstraints):
        self._capacity_constraints = capacity_constraints
        self._time_constraints = time_constraints
        self._priority_constraints = priority_constraints

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return ConstraintsConfig(
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
