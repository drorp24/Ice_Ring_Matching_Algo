from dataclasses import dataclass

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from drop_envelope.slide_service import SlidesServiceWrapper
from geometry.geo2d import Point2D
from geometry.utils import Localizable


class Poin2D(object):
    pass


@dataclass
class DropEnvelopeProperties:
    package_type: PackageType
    drop_azimuth: Angle
    drone_azimuth: Angle
    drop_point: Poin2D


class DropEnvelope(Localizable):
    def __init__(self, drop_envelope_properties: DropEnvelopeProperties):
        self._package_type = drop_envelope_properties.package_type
        self._drop_azimuth = drop_envelope_properties.drop_azimuth
        self._drone_azimuth = drop_envelope_properties.drone_azimuth
        self._drop_point = drop_envelope_properties.drop_point
        self._internal_envelope = SlidesServiceWrapper.get_slide(self._drone_azimuth, self._drop_azimuth,
                                                                 self._package_type).shift(self._drop_point)

    def calc_location(self) -> Point2D:
        return self._internal_envelope.centroid
