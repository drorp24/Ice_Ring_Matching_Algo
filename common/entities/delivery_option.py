from random import Random
from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution
from common.entities.base_entity import BaseEntity
from common.entities.customer_delivery import CustomerDelivery, CustomerDeliveryDistribution


class DeliveryOption(BaseEntity):

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    def __eq__(self, other):
        return self.customer_deliveries == other.customer_deliveries

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries


_DEFAULT_CDD_DISTRIB = [CustomerDeliveryDistribution()]


class DeliveryOptionDistribution(UniformChoiceDistribution):
    def __init__(self, customer_delivery_distributions: List[CustomerDeliveryDistribution] = _DEFAULT_CDD_DISTRIB):
        super().__init__(customer_delivery_distributions)

    def choose_rand(self, random: Random, num_to_choose: int = 1, num_cd: int = 1, num_pdp: int = 1) -> List[
        CustomerDelivery]:
        customer_delivery_distributions = super().choose_rand(random, num_to_choose)
        return [CustomerDelivery(distrib.choose_rand(random, num_cd, num_pdp)) for distrib in
                customer_delivery_distributions]
