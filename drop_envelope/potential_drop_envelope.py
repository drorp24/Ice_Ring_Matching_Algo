from typing import List
from optional import Optional

from common.math.angle import Angle
from drop_envelope.abstract_envelope_collections import ShapeableCollection
from drop_envelope.drop_envelope import DropEnvelope
from drop_envelope.slide_service import _SlidesService, MockSlidesServiceWrapper
from geometry.geo2d import Point2D
from geometry.utils import Shapeable


class PotentialDropEnvelopes(ShapeableCollection):

    def __init__(self, drop_envelopes: List[DropEnvelope], slide_service:_SlidesService = MockSlidesServiceWrapper()):
        assert len(drop_envelopes) == slide_service.drone_azimuth_level_amount
        self._drop_point = drop_envelopes[0].drop_point
        self._drop_azimuth = drop_envelopes[0].drop_azimuth
        self._internal_envelopes = {drop_envelope.drone_azimuth: drop_envelope for drop_envelope in drop_envelopes}

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    @property
    def drop_azimuth(self) -> Optional.of(Angle):
        return self._drop_azimuth

    @property
    def envelopes(self) -> List[DropEnvelope]:
        return list(self._internal_envelopes.values())

    def get_drop_envelope(self, drone_azimuth: Angle) -> DropEnvelope:
        return self._internal_envelopes[drone_azimuth]

    def get_shapeable_collection(self) -> List[Shapeable]:
        return self.envelopes

    def get_centroid(self) -> Point2D:
        return self.drop_point

    def get_arrival_azimuth(self) -> Optional.of(Angle):
        return self.drop_azimuth

