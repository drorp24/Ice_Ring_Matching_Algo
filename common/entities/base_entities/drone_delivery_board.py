from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.drone_delivery import DroneDelivery, DeliveringDrones
from common.entities.base_entities.package import PackageType


class DeliveringDronesBoard(JsonableBaseEntity):
    def __init__(self, delivering_drones_list: [DeliveringDrones]):
        self._delivering_drones_list = delivering_drones_list

    @property
    def delivering_drones_list(self) -> [DeliveringDrones]:
        return self._delivering_drones_list

    def amount_of_formations(self) -> int:
        return len(self._delivering_drones_list)

    def get_max_session_time_per_drone_delivery(self) -> [int]:
        return [drone_delivery.drone_formation.drone_package_configuration.max_session_time
                for drone_delivery in self.delivering_drones_list]

    def get_package_type_amount_per_drone_delivery(self, package_type: PackageType) -> [int]:
        return [drone_delivery.drone_formation.get_package_type_amount(package_type) for drone_delivery in
                self._delivering_drones_list]

    def package_types(self) -> [PackageType]:
        return set([delivering_drones.drone_formation.get_package_type()
                    for delivering_drones in self._delivering_drones_list])

    def max_route_times_in_minutes(self) -> [int]:
        return [delivering_drones.get_max_route_time_in_minutes()
                for delivering_drones in self._delivering_drones_list]

    def __eq__(self, other):
        return self.delivering_drones_list == other.delivering_drones_list

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        # noinspection PyArgumentList
        new_copy = DeliveringDronesBoard(deepcopy(self._delivering_drones_list, memodict))
        memodict[id(self)] = new_copy
        return new_copy

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DeliveringDronesBoard(
            delivering_drones_list=[DeliveringDrones.dict_to_obj(delivering_drones_dict)
                                    for delivering_drones_dict
                                    in dict_input['delivering_drones_list']])


@dataclass
class UnmatchedDeliveryRequest(JsonableBaseEntity):
    graph_index: int
    delivery_request: DeliveryRequest

    def __str__(self):
        return '[UnmatchedDeliveryRequest(graph_index=' + str(self.graph_index) + ', priority=' + str(
            self.delivery_request.priority) + ")]"

    def __hash__(self):
        return hash((self.graph_index, self.delivery_request))

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return UnmatchedDeliveryRequest(
            graph_index=dict_input['graph_index'],
            delivery_request=DeliveryRequest.dict_to_obj(dict_input['delivery_request']))


class DroneDeliveryBoard(JsonableBaseEntity):
    def __init__(self, drone_deliveries: [DroneDelivery], unmatched_delivery_requests: [UnmatchedDeliveryRequest]):
        self._drone_deliveries = drone_deliveries
        self._unmatched_delivery_requests = unmatched_delivery_requests

    @property
    def drone_deliveries(self) -> [DroneDelivery]:
        return self._drone_deliveries

    @property
    def unmatched_delivery_requests(self) -> [UnmatchedDeliveryRequest]:
        return self._unmatched_delivery_requests

    @lru_cache()
    def get_total_work_time_in_minutes(self) -> float:
        return sum([drone_delivery.get_total_work_time_in_minutes() for drone_delivery in self._drone_deliveries])

    @lru_cache()
    def get_total_amount_per_package_type(self) -> PackageTypeAmountMap:
        amount_per_package_type = PackageTypeAmountMap({package: 0 for package in PackageType})
        for drone_delivery in self._drone_deliveries:
            amount_per_package_type.add_packages_to_map(drone_delivery.get_total_package_type_amount_map())
        return amount_per_package_type

    @lru_cache()
    def get_total_priority(self) -> int:
        return sum(drone_delivery.get_total_priority() for drone_delivery in self._drone_deliveries)

    def __eq__(self, other):
        return self.drone_deliveries == other.drone_deliveries \
               and self.unmatched_delivery_requests == other.unmatched_delivery_requests

    def __str__(self):
        drone_deliveries_str = '\n'.join(map(str, self._drone_deliveries))

        unmatched_delivery_requests_str = \
            '\n'.join(map(str, self.unmatched_delivery_requests)) \
                if len(self._unmatched_delivery_requests) > 0 \
                else "[No unmatched delivery requests]"

        return "\n".join((
            f"\n[DroneDeliveryBoard]",
            f"Total amount per package type: {self.get_total_amount_per_package_type()}",
            f"Total work time in minutes: {self.get_total_work_time_in_minutes()}",
            f"Total priority: {self.get_total_priority()}",
            f"Unmatched delivery requests amount: {len(self._unmatched_delivery_requests)}",
            f"{drone_deliveries_str}",
            f"\n{unmatched_delivery_requests_str}"))

    def __hash__(self):
        return hash((tuple(self._drone_deliveries), tuple(self._unmatched_delivery_requests)))

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DroneDeliveryBoard(
            drone_deliveries=[DroneDelivery.dict_to_obj(drone_delivery_dict) for drone_delivery_dict in
                              dict_input['drone_deliveries']],
            unmatched_delivery_requests=[UnmatchedDeliveryRequest.dict_to_obj(unmatched_dict) for unmatched_dict in
                                         dict_input['unmatched_delivery_requests']])
