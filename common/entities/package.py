from __future__ import annotations

import statistics
from enum import Enum

from common.entities.base_entities.distribution import ChoiceDistribution

MAX_POTENTIAL_DROP_ENV_RADIUS_METERS: float = 1000.0
MAX_DELTA_BETWEEN_MIN_AND_MAX_RADIUS: float = 100.0


class PotentialDropEnvelope:

    def __init__(self, minimal_radius_meters: float, maximal_radius_meters: float):
        self._minimal_radius_meters = minimal_radius_meters
        self._maximal_radius_meters = maximal_radius_meters

    @property
    def minimal_radius_meters(self) -> float:
        return self._minimal_radius_meters

    @property
    def maximal_radius_meters(self) -> float:
        return self._maximal_radius_meters

    @property
    def average_radius_meters(self) -> float:
        return statistics.mean([self.maximal_radius_meters,
                                self.minimal_radius_meters])

    def calc_delta_between_radii(self) -> float:
        return self.maximal_radius_meters - self.minimal_radius_meters


class Package:

    def __init__(self, weight: float):
        self._weight = weight
        self._potential_drop_envelope = PotentialDropEnvelope(
            minimal_radius_meters=Package.calc_minimal_radius_meters(weight),
            maximal_radius_meters=Package.calc_max_radius_meters(weight))

    @staticmethod
    def calc_max_radius_meters(weight: float) -> float:
        return Package._normalize_by_weight(MAX_POTENTIAL_DROP_ENV_RADIUS_METERS, weight)

    @staticmethod
    def calc_minimal_radius_meters(weight: float) -> float:
        return Package._normalize_by_weight(MAX_POTENTIAL_DROP_ENV_RADIUS_METERS, weight) - \
               Package._normalize_by_weight(MAX_DELTA_BETWEEN_MIN_AND_MAX_RADIUS, weight)

    @staticmethod
    def _normalize_by_weight(value: float, weight: float) -> float:
        return value / weight

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def potential_drop_envelope(self) -> PotentialDropEnvelope:
        return self._potential_drop_envelope

    def __str__(self):
        return 'package of weight ' + self._weight


class PackageType(Enum):
    TINY = Package(1)
    SMALL = Package(2)
    MEDIUM = Package(4)
    LARGE = Package(8)

    @staticmethod
    def get_all_names():
        return list(PackageType.__members__.keys())


class PackageDistribution(ChoiceDistribution):
    def __init__(self, package_distribution=None):
        if package_distribution is None:
            package_distribution = {}
        super().__init__({package_type: package_distribution.get(package_type, 0)
                          for package_type in PackageType.get_all_names()})


