from __future__ import annotations

import statistics
from enum import Enum

from common.entities.base_entities.base_entity import JsonableBaseEntity

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

    def __init__(self, weight: float, minimal_radius_meters: float, maximal_radius_meters: float):
        self._weight = weight
        self._minimal_radius_meters = minimal_radius_meters
        self._maximal_radius_meters = maximal_radius_meters
        self.__potential_drop_envelope = PotentialDropEnvelope(
            minimal_radius_meters=self._minimal_radius_meters,
            maximal_radius_meters=self._maximal_radius_meters)

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def minimal_radius_meters(self) -> float:
        return self._minimal_radius_meters

    @property
    def maximal_radius_meters(self) -> float:
        return self._maximal_radius_meters

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
        return f'package of weight {str(self._weight)} with rmax of {self.maximal_radius_meters} and rmin of {self.minimal_radius_meters} '


class PackageType(Enum):
    TINY = Package(1, 100, 1000)
    SMALL = Package(2, 100, 1000)
    MEDIUM = Package(4, 100, 1000)
    LARGE = Package(8, 100, 1000)

    @classmethod
    def dict_to_obj(cls, input_dict):
        split_package_type = input_dict['__enum__'].split('.')
        assert (split_package_type[0] == 'PackageType')
        return PackageType[split_package_type[1]]

    def calc_weight(self):
        return self.value.weight

    def get_rmin_rmax(self):
        return self.value.minimal_radius_meters, self.value.maximal_radius_meters

    def __dict__(self):
        return {'__enum__': str(self), 'minimal_radius_meters': self.minimal_radius_meters,
                'maximal_radius_meters': self.maximal_radius_meters}

    def __repr__(self):
        return 'PackageType: ' + str(self.__dict__())

    def __hash__(self):
        return hash(tuple((self.name, self.value)))

    def __eq__(self, other: PackageType):
        return all([self.name == other.name, self.calc_weight() == other.calc_weight(),
                    self.get_rmin_rmax() == other.get_rmin_rmax()])

    def __lt__(self, other: PackageType):
        return self.name < other.name
