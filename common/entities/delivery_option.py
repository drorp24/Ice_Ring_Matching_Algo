import operator
from functools import reduce
from random import Random
from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution, Distribution
from common.entities.base_entity import BaseEntity
from common.entities.customer_delivery import CustomerDelivery, CustomerDeliveryDistribution
from common.utils import list_operation


class DeliveryOption(BaseEntity):

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    def __eq__(self, other):
        return self.customer_deliveries == other.customer_deliveries

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries


class DeliveryOptionDistribution(Distribution):
    def __init__(self, customer_delivery_distributions: List[CustomerDeliveryDistribution]):
        self._customer_delivery_distributions = customer_delivery_distributions

    def choose_rand(self, random: Random, amount: int = 1, num_cd: int = 1, num_pdp: int = 1) -> List[DeliveryOption]:
        cd_distributions = UniformChoiceDistribution(self._customer_delivery_distributions).choose_rand(random, amount)
        return [DeliveryOption(cd_distrib.choose_rand(random, amount=num_cd, num_pdp=num_pdp)) for cd_distrib in cd_distributions]
