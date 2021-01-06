from typing import List

from common.math.angle import Angle, NoneAngle
from drop_envelope.drop_envelope import DropEnvelope
from geometry.geo2d import Point2D


class PotentialDropEnvelopes:
    def __init__(self, drop_envelopes: List[DropEnvelope]):
        assert len(drop_envelopes) >= 1
        self._drop_point = drop_envelopes[0].drop_point
        self._drop_azimuth = drop_envelopes[0].drop_azimuth
        self._internal_envelopes = {drop_envelope.drone_azimuth: drop_envelope for drop_envelope in drop_envelopes}

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    @property
    def drop_azimuth(self) -> [Angle, NoneAngle]:
        return self._drop_azimuth

    @property
    def envelopes(self) -> List[DropEnvelope]:
        return list(self._internal_envelopes.values())

    def get_drop_envelope(self, drone_azimuth: Angle) -> DropEnvelope:
        return self._internal_envelopes[drone_azimuth]