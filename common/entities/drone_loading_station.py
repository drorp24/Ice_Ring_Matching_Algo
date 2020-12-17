from random import Random
from typing import List

from common.entities.base_entity import JsonableBaseEntity
from common.entities.disribution.distribution import Distribution
from geometry.geo2d import Point2D
from geometry.geo_distribution import UniformPointInBboxDistribution, PointLocationDistribution
from geometry.geo_factory import create_point_2d
from common.entities.disribution.distribution import Distribution
from geometry.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import convert_dict_to_point_2d

DEFAULT_LOADING_STATION_LOCATION_DISTRIB = UniformPointInBboxDistribution(0, 100, 0, 100)


class DroneLoadingStation(JsonableBaseEntity):

    def __init__(self, location: Point2D):
        self._location = location

    @property
    def location(self) -> Point2D:
        return self._location

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.location == other.location

    def __hash__(self):
        return hash(self._location)

    @classmethod
    def dict_to_obj(cls, dict_input):
        return DroneLoadingStation(location=convert_dict_to_point_2d(dict_input['location']))


class DroneLoadingStationDistribution(Distribution):

    def __init__(self, drone_station_locations_distribution: PointLocationDistribution = DEFAULT_LOADING_STATION_LOCATION_DISTRIB):
        self._drone_station_locations_distributions = drone_station_locations_distribution

    def choose_rand(self, random: Random, base_location: Point2D = create_point_2d(0,0), amount: int = 1) -> \
            List[DroneLoadingStation]:
        delta_locations = self._drone_station_locations_distributions.choose_rand(random=random, amount=amount)
        locations = [base_location.add_vector(delta.to_vector()) for delta in delta_locations]
        return list(map(DroneLoadingStation, locations))
