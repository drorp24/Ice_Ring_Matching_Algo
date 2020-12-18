from abc import ABC, abstractmethod
from typing import Union

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from geometry.geo2d import Polygon2D, Point2D, EmptyGeometry2D


class EnvelopeServicesInterface(ABC):

    @staticmethod
    def is_valid_envelope(polygon: Polygon2D,minimum_valid_area: float) -> bool:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def calc_drop_envelope(cls, package_type: PackageType, drone_azimuth: Angle, drop_point: Point2D,
                      drop_azimuth: Angle) -> Union[Polygon2D, EmptyGeometry2D]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def calc_delivery_envelope(cls, package_type: PackageType, drone_location: Point2D, drone_azimuth: Angle,
                          drop_azimuth: Angle) -> Union[Polygon2D, EmptyGeometry2D]:
        raise NotImplementedError()
