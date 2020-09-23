from common.entities.package import Package
from geometry.geo2d import Point2D, Vector2D
from geometry.geo_factory import create_point_2d


class _DropPoint:

    def __init__(self, x: float, y: float):
        self._coordinates = create_point_2d(x, y)

    @property
    def coordinates(self) -> Point2D:
        return self._coordinates

    def set_x(self, x: float):
        self._coordinates.x = x

    def set_y(self, y: float):
        self._coordinates.y = y

    def shift(self, v: Vector2D):
        self._coordinates = self._coordinates.add_vector(v)

    def __str__(self):
        return "({},{})".format(self._coordinates.x, self._coordinates.y)


class PackageDeliveryPlan:

    def __init__(self, x: float, y: float, azimuth: float, elevation: float, package: Package):
        self._drop_point = _DropPoint(x, y)
        self._azimuth = azimuth
        self._elevation = elevation
        self._package = package

    @property
    def drop_point(self) -> _DropPoint:
        return self._drop_point

    @property
    def azimuth(self) -> float:
        return self._azimuth

    @property
    def elevation(self) -> float:
        return self._elevation

    @property
    def package(self) -> Package:
        return self._package

    def get_package_type(self) -> str:
        return self._package.type

    def get_package_weight(self) -> float:
        return self._package.weight_kg