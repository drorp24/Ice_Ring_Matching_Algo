from random import Random

from common.entities.base_entities.drone_loading_dock import DroneLoadingDock, \
    create_default_time_window_for_drone_loading_dock
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.entity_distribution.drone_distribution import DroneTypeDistribution
from common.entities.base_entities.entity_distribution.drone_loading_station_distribution import \
    DroneLoadingStationDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeWindowDistribution
from common.entities.distribution.distribution import Distribution, HierarchialDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

DEFAULT_DRONE_LOADING_STATION_DISTRIBUTIONS = DroneLoadingStationDistribution()
DEFAULT_DRONE_TYPE_DISTRIBUTIONS = DroneTypeDistribution()
DEFAULT_TW_DLD_DISTRIB = create_default_time_window_for_drone_loading_dock()


class DroneLoadingDockDistribution(Distribution):

    def __init__(self,
                 drone_type_distribution: DroneTypeDistribution = DEFAULT_DRONE_TYPE_DISTRIBUTIONS,
                 drone_loading_station_distributions: DroneLoadingStationDistribution = DEFAULT_DRONE_LOADING_STATION_DISTRIBUTIONS,
                 time_window_distributions: TimeWindowDistribution = DEFAULT_TW_DLD_DISTRIB,
                 ids: [EntityID] = None):
        self._drone_type_distributions = drone_type_distribution
        self._drone_loading_station_distributions = drone_loading_station_distributions
        self._time_window_distributions = time_window_distributions
        self._ids = ids

    default_amount = 1

    # TODO: make this a HierarchialDistribution that has multiple DroneLoadingStations for each DroneLoadingDock

    def choose_rand(self, random: Random, base_location: Point2D = create_point_2d(0, 0),
                    amount: int = default_amount) -> [DroneLoadingDock]:
        drone_loading_stations = self._drone_loading_station_distributions.choose_rand(random=random,
                                                                                       base_location=base_location,
                                                                                       amount=amount)
        time_windows = self._time_window_distributions.choose_rand(random=random, amount=amount)
        drone_types = self._drone_type_distributions.choose_rand(random=random, amount=amount)
        if self._ids is None:
            self._ids = [EntityID.generate_uuid() for _ in range(amount)]
        else:
            assert (len(self._ids) == amount)
        return [DroneLoadingDock(id_, dl, pt, tw)
                for (id_, dl, pt, tw) in zip(self._ids, drone_loading_stations, drone_types, time_windows)]

    @classmethod
    def distribution_class(cls) -> type:
        return DroneLoadingDock
