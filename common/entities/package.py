from __future__ import annotations

from enum import Enum

maximal_potential_drop_envelope_radius_meters = 1000
maximal_delta_between_minimal_and_maximal_radius_meters = 100


class PotentialDropEnvelope:

    def __init__(self, minimal_radius_meters: float, maximal_radius_meters: float):
        self._minimal_radius_meters = minimal_radius_meters
        self._maximal_radius_meters = maximal_radius_meters

    @property
    def minimal_radius_meters(self):
        return self._minimal_radius_meters

    @property
    def maximal_radius_meters(self):
        return self._maximal_radius_meters


class _Package:

    def __init__(self, size: float):
        self._size = size
        self._potential_drop_envelope = PotentialDropEnvelope(
            minimal_radius_meters=maximal_potential_drop_envelope_radius_meters / size -
            maximal_delta_between_minimal_and_maximal_radius_meters / size,
            maximal_radius_meters=maximal_potential_drop_envelope_radius_meters / size)

    @property
    def size(self):
        return self._size

    @property
    def potential_drop_envelope(self):
        return self._potential_drop_envelope


class PackageType(Enum):
    TINY = _Package(1)
    SMALL = _Package(2)
    MEDIUM = _Package(4)
    LARGE = _Package(8)
