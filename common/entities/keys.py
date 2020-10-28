from attr import dataclass


@dataclass
class DeliveryRequestId:
    delivery_request_id: int


@dataclass
class DeliveryOptionId:
    delivery_option_id: int


@dataclass
class CustomerDeliveryId:
    customer_delivery_id: int


@dataclass
class PackageDeliveryPlanKey:
    delivery_request_id: DeliveryRequestId
    delivery_option_id: DeliveryOptionId
    customer_delivery_id: CustomerDeliveryId
