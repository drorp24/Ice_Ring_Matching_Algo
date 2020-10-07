from common.entities.package import PackageType
from geometry.geo2d import Point2D
from common.math.angle import Angle


class DropPoint:

    def __init__(self, point: Point2D):
        self._coordinates = point

    def __str__(self):
        return "({},{})".format(self._coordinates.x, self._coordinates.y)


class PackageDeliveryPlan:

    def __init__(self, point: Point2D, azimuth: Angle, elevation: Angle, package: PackageType):
        self._drop_point = DropPoint(point)
        self._azimuth = azimuth
        self._elevation = elevation
        self._package = package

    @property
    def drop_point(self) -> DropPoint:
        return self._drop_point

    @property
    def azimuth_deg(self) -> Angle:
        return self._azimuth

    @property
    def elevation_deg(self) -> Angle:
        return self._elevation

    @property
    def package(self) -> PackageType:
        return self._package
