from random import Random
from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlan, PackageDeliveryPlanDistribution


class CustomerDelivery:

    def __init__(self, package_delivery_plans: List[PackageDeliveryPlan]):
        self._package_delivery_plans = package_delivery_plans

    def __eq__(self, other):
        return self.package_delivery_plans == other.package_delivery_plans

    @property
    def package_delivery_plans(self) -> [PackageDeliveryPlan]:
        return self._package_delivery_plans


_DEFAULT_PDP_DISTRIB = [PackageDeliveryPlanDistribution()]


class CustomerDeliveryDistribution(UniformChoiceDistribution):
    def __init__(self, package_delivery_plan_distributions: List[PackageDeliveryPlanDistribution] = _DEFAULT_PDP_DISTRIB):
        super().__init__(package_delivery_plan_distributions)

    def choose_rand(self, random: Random, num_to_choose: int = 1, num_pdp: int = 1) -> [CustomerDelivery]:
        return [CustomerDelivery(distribution.choose_rand(random, num_pdp)) for distribution in super().choose_rand(random, num_to_choose)]
