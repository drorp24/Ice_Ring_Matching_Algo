from random import Random
from typing import List

from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.distribution.distribution import Distribution
from common.entities.base_entities.entity_id import EntityID
from geometry.distribution.geo_distribution import PointLocationDistribution, UniformPointInBboxDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

DEFAULT_LOADING_STATION_LOCATION_DISTRIB = UniformPointInBboxDistribution(0, 100, 0, 100)


class DroneLoadingStationDistribution(Distribution):

    def __init__(self,
                 drone_station_locations_distribution: PointLocationDistribution =
                 DEFAULT_LOADING_STATION_LOCATION_DISTRIB):
        self._drone_station_locations_distributions = drone_station_locations_distribution

    def choose_rand(self, random: Random, base_location: Point2D = create_point_2d(0, 0), amount: int = 1) -> \
            List[DroneLoadingStation]:
        delta_locations = self._drone_station_locations_distributions.choose_rand(random=random, amount=amount)
        locations = [base_location.add_vector(delta.to_vector()) for delta in delta_locations]
        ids = [EntityID.generate_uuid() for delta_location in delta_locations]
        return list(map(DroneLoadingStation, ids, locations))

    @classmethod
    def distribution_class(cls) -> type:
        return DroneLoadingStation
