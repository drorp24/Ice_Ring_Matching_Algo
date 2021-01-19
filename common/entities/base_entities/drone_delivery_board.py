from dataclasses import dataclass
from functools import lru_cache

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import _PackageTypeAmountMap
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

    def get_package_type_amount_per_drone_delivery(self, package_type: PackageType) -> [int]:
        return [drone_delivery.drone_formation.get_package_type_amount(package_type) for drone_delivery in
                self._empty_drone_deliveries]

    def package_types(self) -> [PackageType]:
        return set([edd.drone_formation.get_package_type() for edd in self._empty_drone_deliveries])

    def max_route_times_in_minutes(self) -> [int]:
        return [edd.drone_formation.max_route_times_in_minutes() for edd in self._empty_drone_deliveries]


@dataclass
class UnmatchedDeliveryRequest:
    graph_index: int
    delivery_request: DeliveryRequest

    def __eq__(self, other):
        return self.graph_index == other.graph_index and self.delivery_request == other.delivery_request

    def __str__(self):
        return '[UnmatchedDeliveryRequest(graph_index=' + str(self.graph_index) + ', priority=' + str(
            self.delivery_request.priority) + ")]"

    def __hash__(self):
        return hash((self.graph_index, self.delivery_request))


class DroneDeliveryBoard:
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
    def get_total_amount_per_package_type(self) -> _PackageTypeAmountMap:
        amount_per_package_type = _PackageTypeAmountMap({package: 0 for package in PackageType})
        for drone_delivery in self._drone_deliveries:
            amount_per_package_type.add_to_map(drone_delivery.get_total_package_type_amount_map())
        return amount_per_package_type

    @lru_cache()
    def get_total_priority(self) -> int:
        return sum(drone_delivery.get_total_priority() for drone_delivery in self._drone_deliveries)

    def __eq__(self, other):
        return self.drone_deliveries == other.drone_deliveries \
               and self.unmatched_delivery_requests == other.unmatched_delivery_requests

    def __str__(self):
        drone_deliveries_str = '\n'.join(map(str, self._drone_deliveries))

        unmatched_delivery_requests_str = ''.join(map(str, self.unmatched_delivery_requests)) if len(
            self._unmatched_delivery_requests) > 0 else "[No unmatched delivery requests]"

        return f"\n[DroneDeliveryBoard]\n" \
               f"Total amount per package type: {self.get_total_amount_per_package_type()}\n" \
               f"Total work time in minutes: {self.get_total_work_time_in_minutes()}\n" \
               f"Total priority: {self.get_total_priority()}\n" \
               f"{drone_deliveries_str}\n" \
               f"{unmatched_delivery_requests_str}"

    def __hash__(self):
        return hash((tuple(self._drone_deliveries), tuple(self._unmatched_delivery_requests)))
