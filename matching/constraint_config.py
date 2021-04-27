from common.entities.base_entities.base_entity import JsonableBaseEntity


class PriorityConstraints(JsonableBaseEntity):
    def __init__(self, count_priority_from_zero: bool, priority_cost_coefficient: int):
        self._count_priority_from_zero = count_priority_from_zero
        self._priority_cost_coefficient = priority_cost_coefficient

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return PriorityConstraints(
            count_priority_from_zero=dict_input["count_priority_from_zero"],
            priority_cost_coefficient=dict_input["priority_cost_coefficient"]
        )

    @property
    def count_priority_from_zero(self) -> True:
        return self._count_priority_from_zero

    @property
    def priority_cost_coefficient(self) -> int:
        return self._priority_cost_coefficient

    def __eq__(self, other):
        return self.count_priority_from_zero == other.count_priority_from_zero \
               and self.priority_cost_coefficient == other.priority_cost_coefficient


class TravelTimeConstraints(JsonableBaseEntity):
    def __init__(self, max_waiting_time: int, max_route_time: int, count_time_from_zero: bool,
                 reloading_time: int, important_earliest_coeff: int):
        self._max_waiting_time = max_waiting_time
        self._max_route_time = max_route_time
        self._count_time_from_zero = count_time_from_zero
        self._reloading_time = reloading_time
        self._important_earliest_coeff = important_earliest_coeff

    @property
    def max_waiting_time(self):
        return self._max_waiting_time

    @property
    def max_route_time(self):
        return self._max_route_time

    @property
    def count_time_from_zero(self):
        return self._count_time_from_zero

    @property
    def reloading_time(self):
        return self._reloading_time

    @property
    def important_earliest_coeff(self):
        return self._important_earliest_coeff

    def __eq__(self, other):
        return (self.max_waiting_time == other.max_waiting_time) and \
               (self.max_route_time == other.max_route_time) and \
               (self.count_time_from_zero == other.count_time_from_zero) and \
               (self.reloading_time == other.reloading_time)

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return TravelTimeConstraints(
            max_waiting_time=dict_input["max_waiting_time"],
            max_route_time=dict_input["max_route_time"],
            count_time_from_zero=dict_input["count_time_from_zero"],
            reloading_time=dict_input["reloading_time"],
            important_earliest_coeff=dict_input["important_earliest_coeff"]
        )


class SessionTimeConstraints(JsonableBaseEntity):
    def __init__(self, max_session_time: int):
        self._max_session_time = max_session_time

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return SessionTimeConstraints(
            max_session_time=dict_input["max_session_time"],
        )

    @property
    def max_session_time(self):
        return self._max_session_time

    def __eq__(self, other):
        return self.max_session_time == other.max_session_time


class CapacityConstraints(JsonableBaseEntity):
    def __init__(self, count_capacity_from_zero: bool, capacity_cost_coefficient: int):
        self._count_capacity_from_zero = count_capacity_from_zero
        self._capacity_cost_coefficient = capacity_cost_coefficient

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return CapacityConstraints(
            count_capacity_from_zero=dict_input["count_capacity_from_zero"],
            capacity_cost_coefficient=dict_input["capacity_cost_coefficient"]
        )

    @property
    def count_capacity_from_zero(self) -> bool:
        return self._count_capacity_from_zero

    @property
    def capacity_cost_coefficient(self) -> int:
        return self._capacity_cost_coefficient

    def __eq__(self, other):
        return self.count_capacity_from_zero == other.count_capacity_from_zero \
               and self.capacity_cost_coefficient == other.capacity_cost_coefficient


class ConstraintsConfig(JsonableBaseEntity):
    def __init__(self, capacity_constraints: CapacityConstraints, travel_time_constraints: TravelTimeConstraints,
                 priority_constraints: PriorityConstraints):
        self._capacity_constraints = capacity_constraints
        self._travel_time_constraints = travel_time_constraints
        self._priority_constraints = priority_constraints

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        return ConstraintsConfig(
            capacity_constraints=CapacityConstraints.dict_to_obj(dict_input["capacity"]),
            travel_time_constraints=TravelTimeConstraints.dict_to_obj(dict_input["travel_time"]),
            priority_constraints=PriorityConstraints.dict_to_obj(dict_input["priority"]))

    @property
    def capacity(self) -> CapacityConstraints:
        return self._capacity_constraints

    @property
    def travel_time(self) -> TravelTimeConstraints:
        return self._travel_time_constraints

    @property
    def priority(self) -> PriorityConstraints:
        return self._priority_constraints

    def __eq__(self, other):
        return (self.capacity == other.capacity) and \
               (self.travel_time == other.travel_time) and \
               (self.priority == other.priority)
