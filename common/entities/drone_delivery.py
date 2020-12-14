from dataclasses import dataclass

from common.entities.delivery_request import DeliveryRequest
from common.entities.drone_formation import DroneFormation
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.package import PackageType
from common.entities.temporal import DateTimeExtension


class EmptyDroneDelivery:
    def __init__(self, id_: str, drone_formation: DroneFormation):
        self._id = id_
        self._drone_formation = drone_formation

    def __eq__(self, other):
        return self._id == other.id and self._drone_formation == other.drone_formation

    @property
    def id(self) -> str:
        return self._id

    @property
    def drone_formation(self) -> DroneFormation:
        return self._drone_formation


@dataclass
class MatchedDroneLoadingDock:
    graph_index: int
    drone_loading_dock: DroneLoadingDock
    delivery_min_time: DateTimeExtension
    delivery_max_time: DateTimeExtension

    def __eq__(self, other):
        return self.graph_index == other.graph_index and self.drone_loading_dock == \
               other.drone_loading_dock and self.delivery_min_time == \
               other.delivery_min_time \
               and self.delivery_max_time == other.delivery_max_time

    def __str__(self):
        return 'MatchedDroneLoadingDock(graph_index=' + str(
            self.graph_index) + ', min_time=' + self.delivery_min_time.get_internal().strftime(
            "%m %d %Y %H:%M:%S") + ', max_time=' + self.delivery_max_time.get_internal().strftime(
            "%m %d %Y %H:%M:%S") + ') \n'


@dataclass
class MatchedDeliveryRequest:
    graph_index: int
    package_type: PackageType
    delivery_request: DeliveryRequest
    matched_delivery_option_index: int
    delivery_min_time: DateTimeExtension
    delivery_max_time: DateTimeExtension

    def __eq__(self, other):
        return self.graph_index == other.graph_index and self.delivery_request == other.delivery_request \
               and self.matched_delivery_option_index == other.matched_delivery_option_index \
               and self.delivery_min_time == other.delivery_min_time \
               and self.delivery_max_time == other.delivery_max_time

    # TODO: handle time format
    def __str__(self):
        return 'MatchedDeliveryRequest(graph_index=' + str(self.graph_index) + ', priority=' + str(
            self.delivery_request.priority) + ', min_time=' + self.delivery_min_time.get_internal().strftime(
            "%m %d %Y %H:%M:%S") + ', max_time=' + self.delivery_max_time.get_internal().strftime(
            "%m %d %Y %H:%M:%S") + ', delivered=' + str(
            self.delivery_request.delivery_options[self.matched_delivery_option_index].get_amount_of_package_type(
                self.package_type)) + ')'


# TODO change to MatchedDroneDelivery
class DroneDelivery(EmptyDroneDelivery):
    def __init__(self, id_: str, drone_formation: DroneFormation, matched_requests: [MatchedDeliveryRequest],
                 start_drone_loading_docks: MatchedDroneLoadingDock, end_drone_loading_docks: MatchedDroneLoadingDock):
        super().__init__(id_, drone_formation)
        self._matched_requests = matched_requests
        self._start_drone_loading_docks = start_drone_loading_docks
        self._end_drone_loading_docks = end_drone_loading_docks

        self._total_delivery = 0
        self._total_priority = 0
        self._total_time_in_minutes = 0

        self._set_totals()

    def __eq__(self, other):
        return super().__eq__(
            other) and self._matched_requests == other.matched_requests and self.start_drone_loading_docks == \
               other.start_drone_loading_docks and self.end_drone_loading_docks == other.end_drone_loading_docks

    def __str__(self):
        return "\n[DroneDelivery id=" + self.id + ']\n' + \
               '\n' + str(self.start_drone_loading_docks) + \
               '\n'.join(map(str, self._matched_requests)) + \
               '\n' + str(self.end_drone_loading_docks)

    @property
    def matched_requests(self) -> [MatchedDeliveryRequest]:
        return self._matched_requests

    @property
    def start_drone_loading_docks(self) -> MatchedDroneLoadingDock:
        return self._start_drone_loading_docks

    @property
    def end_drone_loading_docks(self) -> MatchedDroneLoadingDock:
        return self._end_drone_loading_docks

    @property
    def total_time_in_minutes(self) -> float:
        return self._total_time_in_minutes

    @property
    def total_delivery(self) -> int:
        return self._total_delivery

    @property
    def total_priority(self) -> int:
        return self._total_priority

    def _set_totals(self):
        for matched_request in self._matched_requests:
            self._total_delivery += matched_request.delivery_request.delivery_options[
                matched_request.matched_delivery_option_index].get_amount_of_package_type(
                package_type=self.drone_formation.get_platform_type())
            self._total_priority += matched_request.delivery_request.priority

        self._total_time_in_minutes = self._end_drone_loading_docks.delivery_min_time.get_time_delta(
            self._start_drone_loading_docks.delivery_min_time).in_minutes()
