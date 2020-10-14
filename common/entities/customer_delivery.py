from common.entities.grid import CustomerDeliveryId
from common.entities.package_delivery_plan import PackageDeliveryPlan


class CustomerDelivery:

    def __init__(self, customer_delivery_id : CustomerDeliveryId, package_delivery_plans: [PackageDeliveryPlan]):
        self._customer_delivery_id = customer_delivery_id
        self._package_delivery_plans = package_delivery_plans

    @property
    def package_delivery_plans(self) -> [PackageDeliveryPlan]:
        return self._package_delivery_plans
