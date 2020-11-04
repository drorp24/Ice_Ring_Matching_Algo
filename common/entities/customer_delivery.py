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


class CustomerDeliveryDistribution(UniformChoiceDistribution):
    def __init__(self, package_delivery_plan_distributions: List[PackageDeliveryPlanDistribution]):
        super().__init__(package_delivery_plan_distributions)
