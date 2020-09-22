from typing import List

from rafazonscale.common.entities.customer_delivery import CustomerDelivery


class DeliveryOption:

    def __init__(self, customer_deliveries: List[CustomerDelivery]):
        self._type = 'DeliveryOption'
        self._customer_deliveries = customer_deliveries

    @property
    def type(self) -> str:
        return self._type

    @property
    def customer_deliveries(self) -> str:
        return self._customer_deliveries
