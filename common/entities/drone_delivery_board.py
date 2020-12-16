from dataclasses import dataclass

from common.entities.delivery_request import DeliveryRequest
from common.entities.drone import PackageTypesVolumeMap
from common.entities.drone_delivery import DroneDelivery, EmptyDroneDelivery
from common.entities.package import PackageType


class EmptyDroneDeliveryBoard:
    def __init__(self, empty_drone_deliveries: [EmptyDroneDelivery]):
        self._empty_drone_deliveries = empty_drone_deliveries

    @property
    def empty_drone_deliveries(self) -> [EmptyDroneDelivery]:
        return self._empty_drone_deliveries

    def num_of_formations(self) -> int:
        return len(self._empty_drone_deliveries)

    def formation_capacities(self, package_type: PackageType) -> [int]:
        return [delivery.drone_formation.get_package_type_volume(package_type) for delivery in
                self._empty_drone_deliveries]

    def package_types(self) -> [PackageType]:
        return set([edd.drone_formation.get_package_type_formation() for edd in self._empty_drone_deliveries])


@dataclass
class DroppedDeliveryRequest:
    graph_index: int
    delivery_request: DeliveryRequest

    def __eq__(self, other):
        return self.graph_index == other.graph_index and self.delivery_request == other.delivery_request

    def __str__(self):
        return 'DroppedDeliveryRequest(graph_index=' + str(self.graph_index) + ', priority=' + str(
            self.delivery_request.priority) + ',' + self.delivery_request.time_window.since.get_internal().strftime("%m %d %Y %H:%M:%S") \
               + str(self.delivery_request.delivery_options[0].get_amount_per_package_type()) +')'


class DroneDeliveryBoard:
    def __init__(self, drone_deliveries: [DroneDelivery], dropped_delivery_request: [DroppedDeliveryRequest]):
        self._drone_deliveries = drone_deliveries
        self._dropped_delivery_request = dropped_delivery_request

        self._total_amount_per_package_type = None
        self._total_priority = 0
        self._total_time_in_minutes = 0

        self._set_totals()

    def __eq__(self, other):
        return self._drone_deliveries == other.drone_deliveries

    # TODO : add totals to str
    def __str__(self):
        drone_deliveries_str = '\n'.join(map(str, self._drone_deliveries)) if len(
            self._drone_deliveries) > 0 else "\n[No match found]"
        dropped_delivery_request_str = '\n'.join(map(str, self.dropped_delivery_request)) if len(
            self._dropped_delivery_request) > 0 else "\n[No dropped delivery requests]"
        return "\n[DroneDeliveryBoard]\n" + drone_deliveries_str + dropped_delivery_request_str

    @property
    def drone_deliveries(self) -> [DroneDelivery]:
        return self._drone_deliveries

    @property
    def dropped_delivery_request(self) -> [DeliveryRequest]:
        return self._dropped_delivery_request

    @property
    def total_time_in_minutes(self) -> float:
        return self._total_time_in_minutes

    @property
    def total_amount_per_package_type(self) -> PackageTypesVolumeMap:
        return self._total_amount_per_package_type

    @property
    def total_priority(self) -> int:
        return self._total_priority

    def _set_totals(self):
        total_amount_per_package_type = [0] * len(PackageType)

        for drone_delivery in self._drone_deliveries:

            total_amount_per_package_type = [x + y for x, y in zip(total_amount_per_package_type,
                                                                   drone_delivery.total_amount_per_package_type.
                                                                   get_package_types_volumes())]

            self._total_priority += drone_delivery.total_priority
            self._total_time_in_minutes += drone_delivery.total_time_in_minutes

        self._total_amount_per_package_type = PackageTypesVolumeMap(total_amount_per_package_type)
