from dataclasses import dataclass
from typing import Union
from optional import Optional

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from drop_envelope.slide_service import MockSlidesServiceWrapper
from geometry.utils import Shapeable
from geometry.geo2d import Polygon2D, EmptyGeometry2D, Point2D


@dataclass
class DropEnvelopeProperties:
    package_type: PackageType
    drop_azimuth: Angle
    drone_azimuth: Angle
    drop_point: Point2D


class DropEnvelope(Shapeable):
    def __init__(self, drop_envelope_properties: DropEnvelopeProperties):
        self._package_type = drop_envelope_properties.package_type
        self._drop_azimuth = drop_envelope_properties.drop_azimuth
        self._drone_azimuth = drop_envelope_properties.drone_azimuth
        self._drop_point = drop_envelope_properties.drop_point
        self._internal_envelope = MockSlidesServiceWrapper.get_slide(self._drone_azimuth, self._drop_azimuth,
                                                                     self._package_type).shift(self._drop_point)

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    @property
    def drone_azimuth(self) -> Angle:
        return self._drone_azimuth

    @property
    def drop_azimuth(self) -> Angle:
        return self._drop_azimuth

    @property
    def internal_envelope(self) -> Union[Polygon2D, EmptyGeometry2D]:
        return self._internal_envelope

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    def calc_location(self) -> Point2D:
        return self._internal_envelope.centroid

    def get_shape(self) -> Polygon2D:
        return self._internal_envelope

    def calc_area(self) -> float:
        return self._internal_envelope.calc_area()

    def __eq__(self, other):
        return (self.drop_point == other.drop_point and
                self.drop_azimuth == other.drop_azimuth and
                self.drone_azimuth == other.drone_azimuth and
                self.package_type == other.package_type and
                self.internal_envelope == other.internal_envelope)
