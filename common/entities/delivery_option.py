from common.entities.customer_delivery import CustomerDelivery
from common.entities.grid import DeliveryOptionId


class DeliveryOption:

    def __init__(self, delivery_option_id : DeliveryOptionId, customer_deliveries: [CustomerDelivery]):
        self._delivery_option_id = delivery_option_id
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries
