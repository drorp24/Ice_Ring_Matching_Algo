from __future__ import annotations

from common.entities.delivery import Package, _TinyPackage, _SmallPackage, _MediumPackage, _LargePackage, \
    PackageDeliveryPlan

__package_dict = {"Tiny": _TinyPackage(), "Small": _SmallPackage(),
                  "Medium": _MediumPackage(), "Large": _LargePackage()}


def package_factory(package_type: str) -> Package:
    return __package_dict[package_type].clone()


def package_delivery_plan_factory(x: float, y: float, azimuth: float, elevation: float,
                                  package_type: str) -> PackageDeliveryPlan:
    package = package_factory(package_type)
    return PackageDeliveryPlan(x, y, azimuth, elevation, package)
