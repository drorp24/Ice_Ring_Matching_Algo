from __future__ import annotations

import statistics
from enum import Enum
from random import Random
from typing import List

from common.entities.disribution.distribution import ChoiceDistribution
from common.entities.base_entity import JsonableBaseEntity

MAX_POTENTIAL_DROP_ENV_RADIUS_METERS: float = 1000.0
MAX_DELTA_BETWEEN_MIN_AND_MAX_RADIUS: float = 100.0


class PotentialDropEnvelope(JsonableBaseEntity):

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


class Package(JsonableBaseEntity):

    def __init__(self, weight: float):
        self._weight = weight
        self.__potential_drop_envelope = PotentialDropEnvelope(
            minimal_radius_meters=Package.calc_minimal_radius_meters(weight),
            maximal_radius_meters=Package.calc_max_radius_meters(weight))

    @property
    def weight(self) -> float:
        return self._weight

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

    def calc_potential_drop_envelope(self) -> PotentialDropEnvelope:
        return self.__potential_drop_envelope

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

    @classmethod
    def dict_to_obj(cls, input_dict):
        split_package_type = input_dict['__enum__'].split('.')
        assert(split_package_type[0] == 'PackageType')
        return PackageType[split_package_type[1]]

    def __dict__(self):
        return {'__enum__': str(self)}

    def __repr__(self):
        return 'PackageType: ' + str(self.__dict__())


class PackageDistribution(ChoiceDistribution):
    def __init__(self, package_distribution_dict=None):
        if package_distribution_dict is None:
            package_distribution_dict = {}
        super().__init__({package_type: package_distribution_dict.get(package_type, 0)
                          for package_type in PackageType.get_all_names()})

    def choose_rand(self, random: Random, amount=1) -> List[PackageType]:
        package_names = super().choose_rand(random=random, amount=amount)
        return [PackageType[package_name] for package_name in package_names]
