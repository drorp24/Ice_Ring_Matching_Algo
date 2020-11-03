from __future__ import annotations

import statistics
from enum import Enum
from random import Random

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


class PackageType(Enum):
    TINY = Package(1)
    SMALL = Package(2)
    MEDIUM = Package(4)
    LARGE = Package(8)


class ChoiceDistribution:
    def __init__(self, options_to_probability: dict):
        ChoiceDistribution.validate_legal_probs(options_to_probability)
        self.options_to_prob = options_to_probability

    @staticmethod
    def get_safe_probs(probabilities: list):
        sum_probabilities = sum(probabilities)
        if sum_probabilities == 0:
            probabilities = [1.0 / probabilities.__len__()] * probabilities.__len__()
        else:
            probabilities = [prob / sum_probabilities for prob in probabilities]
        return probabilities

    def choose_rand(self, random: Random):
        values = list(self.options_to_prob.keys())
        probs = list(self.options_to_prob.values())
        return random.choices(values, ChoiceDistribution.get_safe_probs(probs))[0]

    def __str__(self):
        return str(self.options_to_prob)

    @staticmethod
    def validate_legal_probs(prob_dict: dict):
        if any([val < 0 for val in prob_dict.values()]):
            raise InvalidProbabilityException()


class PackageDistribution(ChoiceDistribution):
    def __init__(self, package_distribution: dict):
        super().__init__({package_type: package_distribution.get(package_type, 0) for package_type in
                          list(PackageType.__members__.keys())})


class InvalidProbabilityException(Exception):
    pass


if __name__ == "__main__":
    a = PackageDistribution({PackageType.MEDIUM.name: 0.4})
    print(a)
