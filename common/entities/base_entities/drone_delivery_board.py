from dataclasses import dataclass
from functools import lru_cache

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.drone_delivery import DroneDelivery, EmptyDroneDelivery
from common.entities.base_entities.package import PackageType


class EmptyDroneDeliveryBoard:
    def __init__(self, empty_drone_deliveries: [EmptyDroneDelivery]):
        self._empty_drone_deliveries = empty_drone_deliveries

    @property
    def empty_drone_deliveries(self) -> [EmptyDroneDelivery]:
        return self._empty_drone_deliveries

    def amount_of_formations(self) -> int:
        return len(self._empty_drone_deliveries)

    def formation_capacities(self, package_type: PackageType) -> [int]:
        return [delivery.drone_formation.get_package_type_amount(package_type) for delivery in
                self._empty_drone_deliveries]

    def package_types(self) -> [PackageType]:
        return set([edd.drone_formation.get_package_type() for edd in self._empty_drone_deliveries])

    def max_route_times_in_minutes(self) -> [int]:
        return [edd.drone_formation.max_route_times_in_minutes() for edd in self._empty_drone_deliveries]


@dataclass
class DroppedDeliveryRequest:
    graph_index: int
    delivery_request: DeliveryRequest

    def __eq__(self, other):
        return self.graph_index == other.graph_index and self.delivery_request == other.delivery_request

    def __str__(self):
        return '[DroppedDeliveryRequest(graph_index=' + str(self.graph_index) + ', priority=' + str(
            self.delivery_request.priority) + ")]"

    def __hash__(self):
        return hash((self.graph_index, self.delivery_request))


class DroneDeliveryBoard:
    def __init__(self, drone_deliveries: [DroneDelivery], dropped_delivery_requests: [DroppedDeliveryRequest]):
        self._drone_deliveries = drone_deliveries
        self._dropped_delivery_requests = dropped_delivery_requests

    @property
    def drone_deliveries(self) -> [DroneDelivery]:
        return self._drone_deliveries

    @property
    def dropped_delivery_requests(self) -> [DroppedDeliveryRequest]:
        return self._dropped_delivery_requests

    @lru_cache()
    def get_total_work_time_in_minutes(self) -> float:
        return sum([drone_delivery.get_total_work_time_in_minutes() for drone_delivery in self._drone_deliveries])

    @lru_cache()
    def get_total_amount_per_package_type(self) -> PackageTypeAmountMap:
        amount_per_package_type = [0] * len(PackageType)
        for drone_delivery in self._drone_deliveries:
            amount_per_package_type = [total_amount + delivery_amount
                                       for total_amount, delivery_amount
                                       in zip(amount_per_package_type,
                                              drone_delivery.get_total_package_type_amount_map().
                                              get_package_type_amounts())]
        return PackageTypeAmountMap(amount_per_package_type)

    @lru_cache()
    def get_total_priority(self) -> int:
        return sum(drone_delivery.get_total_priority() for drone_delivery in self._drone_deliveries)

    def __eq__(self, other):
        return self.drone_deliveries == other.drone_deliveries \
               and self.dropped_delivery_requests == other.dropped_delivery_requests

    def __str__(self):
        drone_deliveries_str = '\n'.join(map(str, self._drone_deliveries))

        dropped_delivery_requests_str = '\n'.join(map(str, self.dropped_delivery_requests)) if len(
            self._dropped_delivery_requests) > 0 else "\n[No dropped delivery requests]"

        return "\n[DroneDeliveryBoard]\n{drone_deliveries_str}\n{dropped_delivery_request_str}".format(
            drone_deliveries_str=drone_deliveries_str, dropped_delivery_request_str=dropped_delivery_requests_str)

    def __hash__(self):
        return hash((tuple(self._drone_deliveries), tuple(self._dropped_delivery_requests)))
