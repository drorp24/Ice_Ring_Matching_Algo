from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution
from common.entities.customer_delivery import CustomerDelivery, CustomerDeliveryDistribution


class DeliveryOption:

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    def __eq__(self, other):
        return self.customer_deliveries == other.customer_deliveries

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries


class DeliveryOptionDistribution(UniformChoiceDistribution):
    def __init__(self, customer_delivery_distributions: List[CustomerDeliveryDistribution]):
        super().__init__(customer_delivery_distributions)
