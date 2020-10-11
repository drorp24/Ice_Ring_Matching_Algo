from common.entities.package import PackageType
from geometry.geo2d import Point2D
from common.math.angle import Angle


class PackageDeliveryPlan:

    def __init__(self, drop_point: Point2D, azimuth: Angle, elevation: Angle, package: PackageType):
        self._drop_point = drop_point
        self._azimuth = azimuth
        self._elevation = elevation
        self._package = package

    @property
    def drop_point(self) -> Point2D:
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
