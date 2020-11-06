from random import Random
from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution, Distribution
from common.entities.base_entity import BaseEntity
from common.entities.package_delivery_plan import PackageDeliveryPlan, PackageDeliveryPlanDistribution


class CustomerDelivery(BaseEntity):

    def __init__(self, package_delivery_plans: List[PackageDeliveryPlan]):
        self._package_delivery_plans = package_delivery_plans

    def __eq__(self, other):
        return self.package_delivery_plans == other.package_delivery_plans

    @property
    def package_delivery_plans(self) -> [PackageDeliveryPlan]:
        return self._package_delivery_plans


class CustomerDeliveryDistribution(Distribution):
    def __init__(self, package_delivery_plan_distributions: List[PackageDeliveryPlanDistribution]):
        self._pdp_distributions = package_delivery_plan_distributions

    def choose_rand(self, random: Random, amount: int = 1, num_pdp: int = 1) -> List[CustomerDelivery]:
        pdp_distributions = UniformChoiceDistribution(self._pdp_distributions).choose_rand(random, amount=amount)
        return [CustomerDelivery(pdp_distributions[i].choose_rand(random, amount=num_pdp)) for i in list(range(amount))]
