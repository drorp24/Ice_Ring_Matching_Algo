from datetime import date, time, timedelta

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    DateTimeDistribution, TimeWindowDistribution
from common.entities.base_entities.temporal import TimeWindowExtension, Temporal, DateTimeExtension, TimeDeltaExtension
from geometry.geo2d import Point2D
from geometry.utils import Localizable


class DroneLoadingDock(JsonableBaseEntity, Localizable, Temporal):

    def __init__(self,id:EntityID, drone_loading_station: DroneLoadingStation,
                 drone_type: DroneType,
                 time_window: TimeWindowExtension):
        self._id = id
        self._drone_loading_station = drone_loading_station
        self._drone_type = drone_type
        self._time_window = time_window

    @property
    def id(self) -> EntityID :
        return self._id

    @property
    def drone_loading_station(self) -> DroneLoadingStation:
        return self._drone_loading_station

    @property
    def drone_type(self) -> DroneType:
        return self._drone_type

    @property
    def time_window(self) -> TimeWindowExtension:
        return self._time_window

    @property
    def priority(self) -> int:
        return 0

    def calc_location(self) -> Point2D:
        return self.drone_loading_station.location

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DroneLoadingDock(
            id = EntityID.dict_to_obj(dict_input['id']),
            drone_loading_station=DroneLoadingStation.dict_to_obj(dict_input['drone_loading_station']),
            drone_type=DroneType.dict_to_obj(dict_input['drone_type']),
            time_window=TimeWindowExtension.dict_to_obj(dict_input['time_window'])
        )

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self.id == other.id and \
               self.time_window == other.time_window and \
               self.drone_type == other.drone_type and \
               self.drone_loading_station == other.drone_loading_station

    def __hash__(self):
        return hash((self._drone_loading_station, self._drone_type, self._time_window))

    @classmethod
    def dict_to_obj(cls, dict_input):
        return DroneLoadingDock(id=EntityID.dict_to_obj(dict_input['id']),
                                drone_loading_station=DroneLoadingStation.dict_to_obj(dict_input['drone_loading_station']),
                                drone_type=DroneType.dict_to_obj(dict_input['drone_type']),
                                time_window=TimeWindowExtension.dict_to_obj(dict_input['time_window']))


def create_default_time_window_for_drone_loading_dock():
    default_date_time_morning = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))
    default_date_time_night = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(23, 59, 0))
    default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3)),
                                                        TimeDeltaExtension(timedelta(minutes=30))])
    default_dt_options = [default_date_time_morning, default_date_time_night]
    return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)
