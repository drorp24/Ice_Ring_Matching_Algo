from __future__ import annotations

from common.entities.package import PackageType
from common.entities.package_delivery_plan import Angle, PackageDeliveryPlan
from geometry.geo2d import Point2D


def package_delivery_plan_factory(point: Point2D, azimuth: Angle, elevation: Angle,
                                  package_type: PackageType) -> PackageDeliveryPlan:
    return PackageDeliveryPlan(point, azimuth, elevation, package_type)
