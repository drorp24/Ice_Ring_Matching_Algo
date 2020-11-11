from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d
from enum import Enum


class _DroneLoadingStation:

    def __init__(self, location: Point2D):
        self._location = location

    @property
    def location(self) -> Point2D:
        return self._location


class LoadingStations(Enum):
    station_1 = _DroneLoadingStation(create_point_2d(0.0, 0.0))
    station_2 = _DroneLoadingStation(create_point_2d(100.0, 0.0))
    station_3 = _DroneLoadingStation(create_point_2d(0.0, 100.0))
