from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package_factory import package_delivery_plan_factory


def create_customer_delivery(x: float, y: float, azimuth: float, elevation: float,
                             package_type: str) -> CustomerDelivery:
    package_delivery_plan = [package_delivery_plan_factory(x, y, azimuth, elevation, package_type)]
    return CustomerDelivery(package_delivery_plan)


def create_delivery_option(x: float, y: float, azimuth: float, elevation: float,
                           package_type: str) -> DeliveryOption:
    customer_delivery = [create_customer_delivery(x, y, azimuth, elevation, package_type)]
    return DeliveryOption(customer_delivery)


def create_delivery_request(x: float, y: float, azimuth: float, elevation: float,
                            package_type: str, since_time: int, until_time: int, priority: int) -> DeliveryRequest:
    delivery_option = [create_delivery_option(x, y, azimuth, elevation, package_type)]
    return DeliveryRequest(delivery_option, since_time, until_time, priority)