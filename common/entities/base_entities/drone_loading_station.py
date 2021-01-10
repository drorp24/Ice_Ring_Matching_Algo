from geometry.geo2d import Point2D, Polygon2D
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import create_polygon_2d
from geometry.utils import Shapeable

DEFAULT_LOADING_STATION_LOCATION_DISTRIB = UniformPointInBboxDistribution(0, 100, 0, 100)


class DroneLoadingStation(Shapeable):

    def __init__(self, location: Point2D):
        self._location = location

    @property
    def location(self) -> Point2D:
        return self._location

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.location == other.location

    def __hash__(self):
        return hash(self._location)

    def calc_location(self) -> Point2D:
        return self.location

    def get_shape(self) -> Polygon2D:
        return create_polygon_2d([self.location])

    def calc_area(self) -> float:
        return 0

