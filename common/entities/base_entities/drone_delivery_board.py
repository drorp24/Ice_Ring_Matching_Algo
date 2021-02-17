from dataclasses import dataclass
from functools import lru_cache

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.drone_delivery import DroneDelivery, EmptyDroneDelivery
from common.entities.base_entities.package import PackageType


class EmptyDroneDeliveryBoard(JsonableBaseEntity):
    def __init__(self, empty_drone_deliveries: [EmptyDroneDelivery]):
        self._empty_drone_deliveries = empty_drone_deliveries

    @property
    def empty_drone_deliveries(self) -> [EmptyDroneDelivery]:
        return self._empty_drone_deliveries

    def amount_of_formations(self) -> int:
        return len(self._empty_drone_deliveries)

    def get_package_type_amount_per_drone_delivery(self, package_type: PackageType) -> [int]:
        return [drone_delivery.drone_formation.get_package_type_amount(package_type) for drone_delivery in
                self._empty_drone_deliveries]

    def package_types(self) -> [PackageType]:
        return set([edd.drone_formation.get_package_type() for edd in self._empty_drone_deliveries])

    def max_route_times_in_minutes(self) -> [int]:
        return [edd.drone_formation.max_route_times_in_minutes() for edd in self._empty_drone_deliveries]

    def __eq__(self, other):
        return self.empty_drone_deliveries == other.empty_drone_deliveries

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return EmptyDroneDeliveryBoard(
            empty_drone_deliveries=[EmptyDroneDelivery.dict_to_obj(empty_drone_delivery_dict)
                                    for empty_drone_delivery_dict
                                    in dict_input['empty_drone_deliveries']])


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
    def get_total_amount_per_package_type(self) -> PackageTypeAmountMap:
        amount_per_package_type = PackageTypeAmountMap({package: 0 for package in PackageType})
        for drone_delivery in self._drone_deliveries:
            amount_per_package_type.add_to_map(drone_delivery.get_total_package_type_amount_map())
        return amount_per_package_type

    def __eq__(self, other):
        return self.drone_deliveries == other.drone_deliveries \
               and self.unmatched_delivery_requests == other.unmatched_delivery_requests

    def __str__(self):
        drone_deliveries_str = '\n'.join(map(str, self._drone_deliveries))

        unmatched_delivery_requests_str = ''.join(map(str, self.unmatched_delivery_requests)) if len(
            self._unmatched_delivery_requests) > 0 else "[No unmatched delivery requests]"

        return f"\n[DroneDeliveryBoard]\n" \
               f"Total amount per package type: {self.get_total_amount_per_package_type()}\n" \
               f"{drone_deliveries_str}\n" \
               f"{unmatched_delivery_requests_str}"

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
