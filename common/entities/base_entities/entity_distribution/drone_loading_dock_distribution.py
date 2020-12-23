from random import Random
from typing import Dict

from common.entities.base_entities.drone_loading_dock import DroneLoadingDock, \
    create_default_time_window_for_drone_loading_dock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.drone_distribution import PlatformTypeDistribution
from common.entities.base_entities.entity_distribution.drone_loading_station_distribution import \
    DroneLoadingStationDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeWindowDistribution
from common.entities.distribution.distribution import Distribution, HierarchialDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

DEFAULT_DRONE_LOADING_STATION_DISTRIBUTIONS = DroneLoadingStationDistribution()
DEFAULT_PLATFORM_TYPE_DISTRIBUTIONS = PlatformTypeDistribution()
DEFAULT_TW_DLD_DISTRIB = create_default_time_window_for_drone_loading_dock()


class DroneLoadingDockDistribution(Distribution):

    def __init__(self,
                 platform_type_distribution: PlatformTypeDistribution = DEFAULT_PLATFORM_TYPE_DISTRIBUTIONS,
                 drone_loading_station_distributions: DroneLoadingStationDistribution = DEFAULT_DRONE_LOADING_STATION_DISTRIBUTIONS,
                 time_window_distributions: TimeWindowDistribution = DEFAULT_TW_DLD_DISTRIB):
        self._platform_type_distributions = platform_type_distribution
        self._drone_loading_station_distributions = drone_loading_station_distributions
        self._time_window_distributions = time_window_distributions

    default_amount = 1
    # TODO: make this a HierarchialDistribution that has multiple DroneLoadingStations for each DroneLoadingDock

    def choose_rand(self, random: Random, base_location: Point2D = create_point_2d(0, 0),
                    amount: int = default_amount) -> [DroneLoadingDock]:
        drone_loading_stations = self._drone_loading_station_distributions.choose_rand(random=random,
                                                                                       base_location=base_location,
                                                                                       amount=amount)
        time_windows = self._time_window_distributions.choose_rand(random=random, amount=amount)
        platform_types = self._platform_type_distributions.choose_rand(random=random, amount=amount)
        return [DroneLoadingDock(dl, pt, tw)
                for (dl, pt, tw) in zip(drone_loading_stations, platform_types, time_windows)]

    @classmethod
    def distribution_class(cls) -> type:
        return DroneLoadingDock