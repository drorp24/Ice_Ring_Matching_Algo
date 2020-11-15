import itertools
from typing import List

from common.entities.customer_delivery import CustomerDelivery
from common.entities.package_delivery_plan import PackageDeliveryPlan


class DeliveryOption:

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    def __eq__(self, other):
        return self.customer_deliveries == other.customer_deliveries

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries

    @property
    def package_delivery_plans(self) -> List[PackageDeliveryPlan]:
        return list(itertools.chain.from_iterable(
            package_delivery_plan.package_delivery_plans for package_delivery_plan in self._customer_deliveries))
