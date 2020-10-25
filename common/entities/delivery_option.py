from attr import dataclass

from common.entities.customer_delivery import CustomerDelivery


@dataclass
class DeliveryOptionId:
    delivery_option_id: int


class DeliveryOption:

    def __init__(self, delivery_option_id: DeliveryOptionId, customer_deliveries: [CustomerDelivery]):
        self._delivery_option_id = delivery_option_id
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    def __eq__(self, other):
        return self.customer_deliveries == other.customer_deliveries

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries
