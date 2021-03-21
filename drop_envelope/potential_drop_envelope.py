from typing import List
from optional import Optional

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from drop_envelope.azimuth_quantization import get_azimuth_quantization_values
from drop_envelope.drop_envelope import DropEnvelope, DropEnvelopeProperties
from drop_envelope.envelope_collections import ShapeableCollection
from drop_envelope.slide_service import _SlidesService, MockSlidesServiceWrapper
from geometry.geo2d import Point2D, Polygon2D
from geometry.utils import Shapeable


class PotentialDropEnvelopes(ShapeableCollection):

    def __init__(self, drop_point: Point2D, drop_azimuth: Optional.of(Angle),
                 drop_envelopes: List[DropEnvelope]):
        self._drop_point = drop_point
        self._drop_azimuth = drop_azimuth
        self._internal_envelopes = drop_envelopes

    @classmethod
    def from_drop_envelope_properties(cls, drop_azimuth: Optional.of(Angle), package_type: PackageType,
                                      drop_point: Point2D):

        drone_azimuths = get_azimuth_quantization_values(MockSlidesServiceWrapper.drone_azimuth_level_amount)
        drop_envelopes = [DropEnvelope(DropEnvelopeProperties(
                package_type=package_type,
                drop_azimuth=drone_azimuth if drop_azimuth.is_empty() else drop_azimuth.get(),
                drop_point=drop_point,
                drone_azimuth=drone_azimuth)) for drone_azimuth in drone_azimuths]
        drop_envelopes = list(filter(lambda drop_envelope: isinstance(drop_envelope.internal_envelope, Polygon2D),
                                     drop_envelopes))
        return PotentialDropEnvelopes(drop_point=drop_point,
                                      drop_azimuth=drop_azimuth,
                                      drop_envelopes=drop_envelopes)

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    @property
    def drop_azimuth(self) -> Optional.of(Angle):
        return self._drop_azimuth

    @property
    def envelopes(self) -> List[DropEnvelope]:
        return self._internal_envelopes

    def get_shapeables(self) -> List[Shapeable]:
        return self.envelopes

    def get_centroid(self) -> Point2D:
        return self.drop_point
