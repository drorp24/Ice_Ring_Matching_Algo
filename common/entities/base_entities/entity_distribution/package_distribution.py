from __future__ import annotations

from random import Random
from typing import List

from common.entities.base_entities.package import PackageType
from common.entities.distribution.distribution import ChoiceDistribution


class PackageDistribution(ChoiceDistribution):
    def __init__(self, package_distribution_dict={}):
        package_distribution_per_type = {package_type: package_distribution_dict.get(package_type, 0)
         for package_type in PackageType}
        if sum(package_distribution_dict.values()) != sum(package_distribution_per_type.values()):
            raise RuntimeError(
                f"Got invalid package_distribution_dict={package_distribution_dict}. Keys must be of PackageType.")
        super().__init__(package_distribution_per_type)

    def choose_rand(self, random: Random, amount=1) -> List[PackageType]:
        return super().choose_rand(random=random, amount=amount)

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
