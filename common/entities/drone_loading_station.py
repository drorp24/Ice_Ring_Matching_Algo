from random import Random
from typing import List

from common.entities.disribution.distribution import Distribution
from geometry.geo2d import Point2D
from geometry.geo_distribution import UniformPointInBboxDistribution

DEFAULT_DRONE_LOCATIONS_DISTRIB = UniformPointInBboxDistribution(0, 100, 0, 100)


class DroneLoadingStation:

    def __init__(self, location: Point2D):
        self._location = location

    @property
    def location(self) -> Point2D:
        return self._location

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.location == other.location

    def __hash__(self):
        return hash(self._location)


class DroneLoadingStationDistribution(Distribution):

    def __init__(self,
                 drone_station_locations_distributions: UniformPointInBboxDistribution = DEFAULT_DRONE_LOCATIONS_DISTRIB):
        self._drone_station_locations_distributions = drone_station_locations_distributions

    def choose_rand(self, random: Random, amount: int = 1) -> List[DroneLoadingStation]:
        locations = self._drone_station_locations_distributions.choose_rand(random, amount)
        return list(map(DroneLoadingStation, locations))
