from random import Random
from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution, Distribution
from common.entities.base_entity import JsonableBaseEntity
from common.entities.customer_delivery import CustomerDelivery, CustomerDeliveryDistribution, DEFAULT_PDP_DISTRIB


class DeliveryOption(JsonableBaseEntity):

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    def __eq__(self, other):
        return self.customer_deliveries == other.customer_deliveries

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DeliveryOption(
            customer_deliveries=[CustomerDelivery.dict_to_obj(cd_dict) for cd_dict in
                                 dict_input['customer_deliveries']])


DEFAULT_CD_DISTRIB = CustomerDeliveryDistribution([DEFAULT_PDP_DISTRIB])


class DeliveryOptionDistribution(Distribution):
    def __init__(self, customer_delivery_distributions: List[CustomerDeliveryDistribution] = DEFAULT_CD_DISTRIB):
        self._customer_delivery_distributions = customer_delivery_distributions

    def choose_rand(self, random: Random, amount: int = 1, num_cd: int = 1, num_pdp: int = 1) -> List[DeliveryOption]:
        cd_distributions = UniformChoiceDistribution(self._customer_delivery_distributions).choose_rand(random, amount)
        return [DeliveryOption(cd_distributions[i].choose_rand(random, amount=num_cd, num_pdp=num_pdp)) for i in
                list(range(amount))]
