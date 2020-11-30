from datetime import date, timedelta, time
from random import Random

from common.entities.base_entity import JsonableBaseEntity
from common.entities.disribution.distribution import Distribution
from common.entities.drone import PlatformType, PlatformTypeDistribution
from common.entities.drone_loading_station import DroneLoadingStation, DroneLoadingStationDistribution
from common.entities.temporal import TimeWindowExtension, TimeWindowDistribution, DateTimeExtension, \
    TimeDeltaDistribution, TimeDeltaExtension, DateTimeDistribution, Temporal
from geometry.geo2d import Point2D
from geometry.utils import Localizable


class DroneLoadingDock(JsonableBaseEntity, Localizable, Temporal):

    def __init__(self, drone_loading_station: DroneLoadingStation,
                 platform_type: PlatformType,
                 time_window: TimeWindowExtension):
        self._drone_loading_station = drone_loading_station
        self._platform_type = platform_type
        self._time_window = time_window

    @property
    def drone_loading_station(self) -> DroneLoadingStation:
        return self._drone_loading_station

    @property
    def platform_type(self) -> PlatformType:
        return self._platform_type

    @property
    def time_window(self) -> TimeWindowExtension:
        return self._time_window

    @property
    def priority(self) -> int:
        return 0

    def calc_location(self) -> Point2D:
        return self.drone_loading_station.location

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self.time_window == other.time_window and \
               self.platform_type == other.platform_type and \
               self.drone_loading_station == other.drone_loading_station

    def __hash__(self):
        return hash((self._drone_loading_station, self._platform_type, self._time_window))

    @classmethod
    def dict_to_obj(cls, dict_input):
        return DroneLoadingDock(drone_loading_station=DroneLoadingStation.dict_to_obj(dict_input['loading_station']),
                                platform_type=PlatformType.dict_to_obj(dict_input['platform_type']),
                                time_window=TimeWindowExtension.dict_to_obj(dict_input['time_window']))


def create_default_time_window_for_drone_loading_dock():
    default_date_time_morning = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))
    default_date_time_night = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(23, 59, 0))
    default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3)),
                                                        TimeDeltaExtension(timedelta(minutes=30))])
    default_dt_options = [default_date_time_morning, default_date_time_night]
    return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)


DEFAULT_PLATFORM_TYPE_DISTRIBUTIONS = PlatformTypeDistribution()
DEFAULT_TIME_WINDOW_DISTRIBUTIONS = create_default_time_window_for_drone_loading_dock()
DEFAULT_DRONE_LOADING_STATION_DISTRIBUTIONS = DroneLoadingStationDistribution()


class DroneLoadingDockDistribution(Distribution):

    def __init__(self, platform_type_distribution: PlatformTypeDistribution = DEFAULT_PLATFORM_TYPE_DISTRIBUTIONS,
                 drone_loading_station_distributions: DroneLoadingStationDistribution =
                 DEFAULT_DRONE_LOADING_STATION_DISTRIBUTIONS,
                 time_window_distributions: TimeWindowDistribution =
                 DEFAULT_TIME_WINDOW_DISTRIBUTIONS):
        self._platform_type_distributions = platform_type_distribution
        self._drone_loading_station_distributions = drone_loading_station_distributions
        self._time_window_distributions = time_window_distributions

    def choose_rand(self, random: Random, amount: int = 1) -> [DroneLoadingDock]:
        drone_loading_stations = self._drone_loading_station_distributions.choose_rand(random, amount)
        time_windows = self._time_window_distributions.choose_rand(random, amount)
        platform_types = self._platform_type_distributions.choose_rand(random, amount)
        return [DroneLoadingDock(dl, pt, tw)
                for (dl, pt, tw) in zip(drone_loading_stations, platform_types, time_windows)]
