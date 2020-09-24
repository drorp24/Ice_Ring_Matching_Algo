from time_window import TimeWindow

from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import Angle, PackageDeliveryPlan
from geometry.geo2d import Point2D


def create_customer_delivery(point: Point2D, azimuth: Angle, elevation: Angle,
                             package: PackageType) -> CustomerDelivery:
    package_delivery_plan = [PackageDeliveryPlan(point, azimuth, elevation, package)]
    return CustomerDelivery(package_delivery_plan)


def create_delivery_option(point: Point2D, azimuth: Angle, elevation: Angle,
                           package: PackageType) -> DeliveryOption:
    customer_delivery = [create_customer_delivery(point, azimuth, elevation, package)]
    return DeliveryOption(customer_delivery)


def create_delivery_request(point: Point2D, azimuth: Angle, elevation: Angle,
                            package: PackageType, time_window: TimeWindow, priority: int) -> DeliveryRequest:
    delivery_option = [create_delivery_option(point, azimuth, elevation, package)]
    return DeliveryRequest(delivery_option, time_window, priority)
