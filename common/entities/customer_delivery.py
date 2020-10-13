from common.entities.package_delivery_plan import PackageDeliveryPlan


class CustomerDelivery:

    def __init__(self, package_delivery_plans: [PackageDeliveryPlan]):
        self._package_delivery_plans = package_delivery_plans

    @property
    def package_delivery_plans(self) -> [PackageDeliveryPlan]:
        return self._package_delivery_plans
