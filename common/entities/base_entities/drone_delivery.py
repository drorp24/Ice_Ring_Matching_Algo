from dataclasses import dataclass
from functools import lru_cache

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.drone_formation import DroneFormation
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeWindowExtension

DEFAULT_MAX_ROUTE_TIME_IN_MINUTES = 1440
DEFAULT_VELOCITY_METER_PER_SEC = 10.0


class DeliveringDrones(JsonableBaseEntity):
    def __init__(self, id_: EntityID, drone_formation: DroneFormation,
                 start_loading_dock: DroneLoadingDock, end_loading_dock: DroneLoadingDock,
                 max_route_time_in_minutes: int = DEFAULT_MAX_ROUTE_TIME_IN_MINUTES,
                 velocity_meter_per_sec: float = DEFAULT_VELOCITY_METER_PER_SEC):
        if drone_formation.get_drone_type() != start_loading_dock.drone_type:
            raise TypeError(f"The Drone formation's drone_type {drone_formation.get_drone_type()} "
                            f"is not equal to start_loading_dock's drone_type {start_loading_dock.drone_type}")
        if drone_formation.get_drone_type() != end_loading_dock.drone_type:
            raise TypeError(f"The Drone formation's drone_type {drone_formation.get_drone_type()} "
                            f"is not equal to end_loading_dock's drone_type {end_loading_dock.drone_type}")
        self._id = id_
        self._drone_formation = drone_formation
        self._start_loading_dock = start_loading_dock
        self._end_loading_dock = end_loading_dock
        self._max_route_time_in_minutes = max_route_time_in_minutes  # TODO: Change to real endurance
        self._velocity_meter_per_sec = velocity_meter_per_sec  # TODO: Change to real velocity

    @property
    def id(self) -> EntityID:
        return self._id

    @property
    def drone_formation(self) -> DroneFormation:
        return self._drone_formation

    @property
    def start_loading_dock(self) -> DroneLoadingDock:
        return self._start_loading_dock

    @property
    def end_loading_dock(self) -> DroneLoadingDock:
        return self._end_loading_dock

    @property
    def max_route_time_in_minutes(self) -> int:
        return self._max_route_time_in_minutes

    @property
    def velocity_meter_per_sec(self) -> float:
        return self._velocity_meter_per_sec

    def get_formation_max_range_in_meters(self) -> float:
        return self.velocity_meter_per_sec * self.max_route_time_in_minutes * 60.0

    def __eq__(self, other):
        return all([self.id == other.id,
                   self.drone_formation == other.drone_formation,
                   self.start_loading_dock == other.start_loading_dock,
                   self.end_loading_dock == other.end_loading_dock,
                   self.max_route_time_in_minutes == other.max_route_time_in_minutes,
                   self.velocity_meter_per_sec == other.velocity_meter_per_sec])

    def __hash__(self):
        return hash((
            self.id,
            self.drone_formation,
            self.start_loading_dock,
            self.end_loading_dock,
            self.max_route_time_in_minutes,
            self.velocity_meter_per_sec
        ))

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DeliveringDrones(id_=EntityID.dict_to_obj(dict_input['id']),
                                drone_formation=DroneFormation.dict_to_obj(dict_input['drone_formation']),
                                start_loading_dock=DroneLoadingDock.dict_to_obj(dict_input['start_loading_dock']),
                                end_loading_dock=DroneLoadingDock.dict_to_obj(dict_input['end_loading_dock']),
                                max_route_time_in_minutes=int(dict_input['max_route_time_in_minutes']),
                                velocity_meter_per_sec=float(dict_input['velocity_meter_per_sec']),
                                )


@dataclass
class MatchedDroneLoadingDock(JsonableBaseEntity):
    graph_index: int  # TODO: replace to DeliveryRequestUUID
    drone_loading_dock: DroneLoadingDock
    delivery_time_window: TimeWindowExtension

    def __str__(self):
        return '[MatchedDroneLoadingDock(graph_index=' + str(
            self.graph_index) + ', min_time=' + self.delivery_time_window.since.str_format_time() + \
               ', max_time=' + self.delivery_time_window.until.str_format_time() + ')]'

    def __hash__(self):
        return hash((self.graph_index, self.drone_loading_dock,
                     self.delivery_time_window.since, self.delivery_time_window.until))

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return MatchedDroneLoadingDock(
            graph_index=dict_input['graph_index'],
            drone_loading_dock=DroneLoadingDock.dict_to_obj(dict_input['drone_loading_dock']),
            delivery_time_window=TimeWindowExtension.dict_to_obj(dict_input['delivery_time_window']))


@dataclass
class MatchedDeliveryRequest(JsonableBaseEntity):
    graph_index: int
    delivery_request: DeliveryRequest
    matched_delivery_option_index: int  # TODO: replace to DeliveryOptionUUID
    delivery_time_window: TimeWindowExtension

    def __str__(self):
        return '[MatchedDeliveryRequest(graph_index=' + str(self.graph_index) + ', priority=' + str(
            self.delivery_request.priority) + ', min_time=' + self.delivery_time_window.since.str_format_time() + \
               ', max_time=' + self.delivery_time_window.until.str_format_time() + ', delivered=' + str(
            self.delivery_request.delivery_options[
                self.matched_delivery_option_index].get_package_type_amount_map()) + ')]'

    def __hash__(self):
        return hash((self.graph_index, self.delivery_request, self.matched_delivery_option_index,
                     self.delivery_time_window.since, self.delivery_time_window.until))

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return MatchedDeliveryRequest(
            graph_index=dict_input['graph_index'],
            delivery_request=DeliveryRequest.dict_to_obj(dict_input['delivery_request']),
            matched_delivery_option_index=dict_input['matched_delivery_option_index'],
            delivery_time_window=TimeWindowExtension.dict_to_obj(dict_input['delivery_time_window']))


class DroneDelivery(JsonableBaseEntity):
    def __init__(self, delivering_drones: DeliveringDrones,
                 matched_requests: [MatchedDeliveryRequest],
                 start_drone_loading_docks: MatchedDroneLoadingDock,
                 end_drone_loading_docks: MatchedDroneLoadingDock):
        self._delivering_drones = delivering_drones
        self._matched_requests = matched_requests
        self._start_drone_loading_docks = start_drone_loading_docks
        self._end_drone_loading_docks = end_drone_loading_docks

    @property
    def delivering_drones(self) -> DeliveringDrones:
        return self._delivering_drones

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
    def get_total_package_type_amount_map(self) -> PackageTypeAmountMap:
        amount_per_package_type = PackageTypeAmountMap({package: 0 for package in PackageType})
        for matched_request in self._matched_requests:
            dr = matched_request.delivery_request
            delivery_option_of_interest = dr.delivery_options[matched_request.matched_delivery_option_index]
            delivery_option_package_type_amount = delivery_option_of_interest.get_package_type_amount_map()
            amount_per_package_type.add_to_map(delivery_option_package_type_amount)
        return amount_per_package_type

    @lru_cache()
    def get_total_priority(self) -> int:
        return sum(matched_request.delivery_request.priority for matched_request in self._matched_requests)

    def __str__(self):
        if len(self._matched_requests) == 0:
            return "\n[DroneDelivery id={id} - origin {origin_capacity} No match found]".format(
                id=self.delivering_drones.id,
                origin_capacity=self.delivering_drones.drone_formation.get_package_type_amount_map(), )

        return "\n[DroneDelivery id={id} origin {origin_capacity} matched " \
               "{total_amount_per_package_type} total priority={priority} total time in " \
               "minutes={total_time}]\n{start_drone_loading_docks}\n{matched_requests}\n{end_drone_loading_docks}" \
            .format(id=self.delivering_drones.id,
                    origin_capacity=self.delivering_drones.drone_formation.get_package_type_amount_map(),
                    total_amount_per_package_type=str(self.get_total_package_type_amount_map()),
                    priority=str(self.get_total_priority()),
                    total_time=str(self.get_total_work_time_in_minutes()),
                    start_drone_loading_docks=str(self.start_drone_loading_docks),
                    matched_requests='\n'.join(map(str, self._matched_requests)),
                    end_drone_loading_docks=str(self.end_drone_loading_docks))

    def __hash__(self):
        return hash((self._delivering_drones, tuple(self._matched_requests),
                     self._start_drone_loading_docks, self._end_drone_loading_docks))

    def __eq__(self, other):
        return all([self.delivering_drones == other.delivering_drones,
                    self._matched_requests == other.matched_requests,
                    self.start_drone_loading_docks == other.start_drone_loading_docks,
                    self.end_drone_loading_docks == other.end_drone_loading_docks])

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DroneDelivery(
            delivering_drones=DeliveringDrones.dict_to_obj(dict_input['delivering_drones']),
            matched_requests=[MatchedDeliveryRequest.dict_to_obj(matched_request_dict) for matched_request_dict in
                              dict_input['matched_requests']],
            start_drone_loading_docks=MatchedDroneLoadingDock.dict_to_obj(dict_input['start_drone_loading_docks']),
            end_drone_loading_docks=MatchedDroneLoadingDock.dict_to_obj(dict_input['end_drone_loading_docks']))
