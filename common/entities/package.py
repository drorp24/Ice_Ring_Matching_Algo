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


class PackageType(Enum):
    TINY = 1
    SMALL = 2
    MEDIUM = 4
    LARGE = 8


class Package:

    def __init__(self, package_type: PackageType):
        self._package_type = package_type
        self._potential_drop_envelope = PotentialDropEnvelope(
            minimal_radius_meters=maximal_potential_drop_envelope_radius_meters / package_type.value -
            maximal_delta_between_minimal_and_maximal_radius_meters / package_type.value,
            maximal_radius_meters=maximal_potential_drop_envelope_radius_meters / package_type.value)

    @property
    def type(self):
        return self._package_type

    @property
    def potential_drop_envelope(self):
        return self._potential_drop_envelope
