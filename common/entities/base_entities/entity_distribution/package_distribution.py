from __future__ import annotations

from random import Random
from typing import List

from common.entities.base_entities.package import PackageType
from common.entities.distribution.distribution import ChoiceDistribution


class PackageDistribution(ChoiceDistribution):
    def __init__(self, package_distribution_dict={}):
        super().__init__({package_type.name: package_distribution_dict.get(package_type.name, 0)
                          for package_type in PackageType})

    def choose_rand(self, random: Random, amount=1) -> List[PackageType]:
        package_names = super().choose_rand(random=random, amount=amount)
        return [PackageType[package_name] for package_name in package_names]

    @classmethod
    def distribution_class(cls) -> type:
        return PackageType