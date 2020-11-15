from typing import List

from common.entities.package_delivery_plan import PackageDeliveryPlan


class CustomerDelivery:

    def __init__(self, package_delivery_plans: List[PackageDeliveryPlan]):
        self._package_delivery_plans = package_delivery_plans

    def __eq__(self, other):
        return self.package_delivery_plans == other.package_delivery_plans

    @property
    def package_delivery_plans(self) -> List[PackageDeliveryPlan]:
        return self._package_delivery_plans
