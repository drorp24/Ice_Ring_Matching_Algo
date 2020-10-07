from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle
from geometry.geo2d import Point2D


def package_delivery_plan_factory(point: Point2D, azimuth: Angle, elevation: Angle,
                                  package: PackageType) -> PackageDeliveryPlan:
    return PackageDeliveryPlan(point, azimuth, elevation, package.value)
