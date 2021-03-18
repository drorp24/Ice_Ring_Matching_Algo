from __future__ import annotations

from abc import ABC, abstractmethod

from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.package import PackageType


class PackageHolder(ABC):

    @abstractmethod
    def get_package_type_amount(self, package_type: PackageType) -> int:
        raise NotImplementedError()

    def get_package_type_amount_map(self) -> PackageTypeAmountMap:
        return PackageTypeAmountMap(
            {package_type: self.get_package_type_amount(package_type) for package_type in PackageType})

    def has_at_least_one_identical(self, other) -> bool:
        return True if len(
            set(self.get_package_type_amount_map().get_active_package_types()).intersection(
                set(other.get_package_type_amount_map().get_active_package_types()))) > 0 else False
