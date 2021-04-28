from __future__ import annotations

import statistics
from enum import Enum

from common.entities.base_entities.base_entity import JsonableBaseEntity


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
        self.__potential_drop_envelope = PotentialDropEnvelope(
            minimal_radius_meters=minimal_radius_meters,
            maximal_radius_meters=maximal_radius_meters)

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def minimal_radius_meters(self) -> float:
        return self.__potential_drop_envelope.minimal_radius_meters

    @property
    def maximal_radius_meters(self) -> float:
        return self.__potential_drop_envelope.maximal_radius_meters

    def calc_potential_drop_envelope(self) -> PotentialDropEnvelope:
        return self.__potential_drop_envelope

    def __str__(self):
        return f'package of weight: {str(self._weight)},potential drop env of: {str(self.__potential_drop_envelope)}'


class PackageType(Enum):
    TINY = Package(weight=1, minimal_radius_meters=900, maximal_radius_meters=1000)
    SMALL = Package(weight=2, minimal_radius_meters=450, maximal_radius_meters=500)
    MEDIUM = Package(weight=4, minimal_radius_meters=225, maximal_radius_meters=250)
    LARGE = Package(weight=8, minimal_radius_meters=112.5, maximal_radius_meters=125)

    @classmethod
    def dict_to_obj(cls, input_dict):
        split_package_type = input_dict['__enum__'].split('.')
        assert (split_package_type[0] == 'PackageType')
        return PackageType[split_package_type[1]]

    def calc_weight(self):
        return self.value.weight

    def get_rmin(self):
        return PackageType.TINY.value.rmin

    def get_rmax(self):
        return PackageType.TINY.value.rmax

    def __dict__(self):
        return {'__enum__': str(self)}

    def __repr__(self):
        return 'PackageType: ' + str(self.__dict__())

    def __hash__(self):
        return hash(tuple((self.name, self.value)))

    def __eq__(self, other: PackageType):
        return all([self.name == other.name, self.calc_weight() == other.calc_weight(),
                    self.calc_potential_drop_envelope() == other.calc_potential_drop_envelope()])

    def __lt__(self, other: PackageType):
        return self.name < other.name
