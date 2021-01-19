from dataclasses import dataclass
from functools import lru_cache

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import _PackageTypeAmountMap
from common.entities.base_entities.drone_formation import DroneFormation
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeWindowExtension


class EmptyDroneDelivery:
    def __init__(self, id_: EntityID, drone_formation: DroneFormation):
        self._id = id_
        self._drone_formation = drone_formation

    def __eq__(self, other):
        return self._id == other.id and self._drone_formation == other.drone_formation

    def __hash__(self):
        return hash((self._id, self._drone_formation))

    @property
    def id(self) -> EntityID:
        return self._id

    @property
    def drone_formation(self) -> DroneFormation:
        return self._drone_formation


@dataclass
class MatchedDroneLoadingDock:
    graph_index: int  # TODO: replace to DeliveryRequestUUID
    drone_loading_dock: DroneLoadingDock
    delivery_time_window: TimeWindowExtension

    def __eq__(self, other):
        return self.graph_index == other.graph_index and self.drone_loading_dock == \
               other.drone_loading_dock and self.delivery_time_window.since == \
               other.delivery_time_window.since \
               and self.delivery_time_window.until == other.delivery_time_window.until

    def __str__(self):
        return '[MatchedDroneLoadingDock(graph_index=' + str(
            self.graph_index) + ', min_time=' + self.delivery_time_window.since.str_format_time() + \
               ', max_time=' + self.delivery_time_window.until.str_format_time() + ')]'

    def __hash__(self):
        return hash((self.graph_index, self.drone_loading_dock,
                     self.delivery_time_window.since, self.delivery_time_window.until))


@dataclass
class MatchedDeliveryRequest:
    graph_index: int
    delivery_request: DeliveryRequest
    matched_delivery_option_index: int  # TODO: replace to DeliveryOptionUUID
    delivery_time_window: TimeWindowExtension

    def __eq__(self, other):
        return self.graph_index == other.graph_index and self.delivery_request == other.delivery_request \
               and self.matched_delivery_option_index == other.matched_delivery_option_index \
               and self.delivery_time_window.since == other.delivery_time_window.since \
               and self.delivery_time_window.until == other.delivery_time_window.until

    def __str__(self):
        return '[MatchedDeliveryRequest(graph_index=' + str(self.graph_index) + ', priority=' + str(
            self.delivery_request.priority) + ', min_time=' + self.delivery_time_window.since.str_format_time() + \
               ', max_time=' + self.delivery_time_window.until.str_format_time() + ', delivered=' + str(
            self.delivery_request.delivery_options[
                self.matched_delivery_option_index].get_package_type_amount_map()) + ')]'

    def __hash__(self):
        return hash((self.graph_index, self.delivery_request, self.matched_delivery_option_index,
                     self.delivery_time_window.since, self.delivery_time_window.until))


# TODO change to MatchedDroneDelivery
class DroneDelivery(EmptyDroneDelivery):
    def __init__(self, id_: EntityID, drone_formation: DroneFormation,
                 matched_requests: [MatchedDeliveryRequest],
                 start_drone_loading_docks: MatchedDroneLoadingDock,
                 end_drone_loading_docks: MatchedDroneLoadingDock):
        super().__init__(id_, drone_formation)
        self._matched_requests = matched_requests
        self._start_drone_loading_docks = start_drone_loading_docks
        self._end_drone_loading_docks = end_drone_loading_docks

    @property
    def matched_requests(self) -> [MatchedDeliveryRequest]:
        return self._matched_requests

    @property
    def start_drone_loading_docks(self) -> MatchedDroneLoadingDock:
        return self._start_drone_loading_docks

    @property
    def end_drone_loading_docks(self) -> MatchedDroneLoadingDock:
        return self._end_drone_loading_docks

    @lru_cache()
    def get_total_work_time_in_minutes(self) -> float:
        return self._end_drone_loading_docks.delivery_time_window.since.get_time_delta(
            self._start_drone_loading_docks.delivery_time_window.since).in_minutes()

    @lru_cache()
    def get_total_package_type_amount_map(self) -> _PackageTypeAmountMap:
        amount_per_package_type = _PackageTypeAmountMap({package.name: 0 for package in PackageType})
        for matched_request in self._matched_requests:
            dr = matched_request.delivery_request
            do = dr.delivery_options[matched_request.matched_delivery_option_index]
            ptam = do.get_package_type_amount_map()
            amount_per_package_type.add_to_map(ptam)
        return amount_per_package_type


        # for matched_request in self._matched_requests:
        #     m = matched_request.delivery_request.delivery_options[matched_request.matched_delivery_option_index]\
        #         .get_package_type_amount_map()
        #     amount_per_package_type = [total_amount + request_amount
        #                                for total_amount, request_amount
        #                                in zip(amount_per_package_type.values(), m)]
        # return _PackageTypeAmountMap(amount_per_package_type)

    @lru_cache()
    def get_total_priority(self) -> int:
        return sum(matched_request.delivery_request.priority for matched_request in self._matched_requests)

    def __str__(self):
        if len(self._matched_requests) == 0:
            return "\n[DroneDelivery id={id} - origin {origin_capacity} No match found]".format(
                id=self.id,
                origin_capacity=self.drone_formation.get_package_type_amount_map(), )

        return "\n[DroneDelivery id={id} origin {origin_capacity} matched " \
               "{total_amount_per_package_type} total priority={priority} total time in " \
               "minutes={total_time}]\n{start_drone_loading_docks}\n{matched_requests}\n{end_drone_loading_docks}" \
            .format(id=self.id,
                    origin_capacity=self.drone_formation.get_package_type_amount_map(),
                    total_amount_per_package_type=str(self.get_total_package_type_amount_map()),
                    priority=str(self.get_total_priority()), total_time=str(self.get_total_work_time_in_minutes()),
                    start_drone_loading_docks=str(self.start_drone_loading_docks),
                    matched_requests='\n'.join(map(str, self._matched_requests)),
                    end_drone_loading_docks=str(self.end_drone_loading_docks))

    def __hash__(self):
        return hash((tuple(self._matched_requests),
                     self._start_drone_loading_docks, self._end_drone_loading_docks))

    def __eq__(self, other):
        return super().__eq__(
            other) and self._matched_requests == other.matched_requests and self.start_drone_loading_docks == \
               other.start_drone_loading_docks and self.end_drone_loading_docks == other.end_drone_loading_docks
