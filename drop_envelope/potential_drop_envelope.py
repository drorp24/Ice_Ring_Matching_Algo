from typing import List
from optional import Optional

from common.math.angle import Angle
from drop_envelope.drop_envelope import DropEnvelope
from drop_envelope.slide_service import _SlidesService, MockSlidesServiceWrapper
from geometry.geo2d import Point2D


class PotentialDropEnvelopes:

    def __init__(self, drop_point: Point2D, drop_azimuth: Optional.of(Angle),
                 drop_envelopes: List[DropEnvelope], slide_service:_SlidesService = MockSlidesServiceWrapper()):
        assert len(drop_envelopes) == slide_service.drone_azimuth_level_amount
        self._drop_point = drop_point
        self._drop_azimuth = drop_azimuth
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
