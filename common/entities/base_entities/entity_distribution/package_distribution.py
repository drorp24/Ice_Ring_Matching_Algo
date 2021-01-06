from __future__ import annotations

from random import Random
from typing import List

from common.entities.base_entities.package import PackageType
from common.entities.distribution.distribution import ChoiceDistribution


class PackageDistribution(ChoiceDistribution):
    def __init__(self, package_distribution_dict={}):
        super().__init__({package_type: package_distribution_dict.get(package_type, 0)
                          for package_type in PackageType.get_all_names()})

    def choose_rand(self, random: Random, amount=1) -> List[PackageType]:
        package_names = super().choose_rand(random=random, amount=amount)
        return [PackageType[package_name] for package_name in package_names]

    @classmethod
    def distribution_class(cls) -> type:
        return PackageType


class ExactPackageDistribution(PackageDistribution):
    def __init__(self, package_types: List[PackageType]):
        self._package_types = package_types
        self._amount_count = 0

    def choose_rand(self, random: Random, amount=1) -> List[PackageType]:
        if self._amount_count + amount > len(self._package_types):
            raise RuntimeError(
                f"Used {self._amount_count} randomized choices which is \
                more than the initially given {len(self._package_types)} ")
        choices = self._package_types[self._amount_count: self._amount_count + amount]
        self._amount_count += amount
        return choices

    @classmethod
    def distribution_class(cls) -> type:
        return PackageType
