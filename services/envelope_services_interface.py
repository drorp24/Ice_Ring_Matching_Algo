from abc import ABC, abstractmethod

from common.entities.package import PackageType
from common.math.angle import Angle
from geometry.geo2d import Polygon2D, Point2D


class EnvelopeServicesInterface(ABC):

    @classmethod
    @abstractmethod
    def drop_envelope(cls, package_type: PackageType, drone_azimuth: Angle, drop_point: Point2D,
                      drop_azimuth: Angle) -> Polygon2D:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def delivery_envelope(cls, package_type: PackageType, drone_location: Point2D, drone_azimuth: Angle,
                          drop_azimuth: Angle) -> Polygon2D:
        raise NotImplementedError()
