from geometry.geo2d import Point2D
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution

DEFAULT_LOADING_STATION_LOCATION_DISTRIB = UniformPointInBboxDistribution(0, 100, 0, 100)


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
