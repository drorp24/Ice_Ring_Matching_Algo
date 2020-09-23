from __future__ import annotations

from common.entities.package import Package, _TinyPackage, _SmallPackage, _MediumPackage, _LargePackage
from common.entities.package_delivery_plan import PackageDeliveryPlan

__package_dict = {"Tiny": _TinyPackage(), "Small": _SmallPackage(),
                  "Medium": _MediumPackage(), "Large": _LargePackage()}


def package_factory(package_type: str) -> Package:
    if __package_dict.get(package_type) is not None:
        return __package_dict[package_type].clone()
    return None


def package_delivery_plan_factory(x: float, y: float, arrival_angle: float, hitting_angle: float,
                                  package_type: str) -> PackageDeliveryPlan:
    package = package_factory(package_type)
    return PackageDeliveryPlan(x, y, arrival_angle, hitting_angle, package)
