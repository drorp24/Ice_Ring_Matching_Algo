from random import Random
from typing import List

from common.entities.base_entity import JsonableBaseEntity
from common.entities.disribution.distribution import UniformChoiceDistribution, Distribution
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan, PackageDeliveryPlanDistribution, \
    DEFAULT_DROP_POINT_DISTRIB, DEFAULT_AZI_DISTRIB, DEFAULT_PITCH_DISTRIB, DEFAULT_PACKAGE_DISTRIB
from geometry.geo2d import Point2D
from geometry.geo_factory import calc_centroid


class CustomerDelivery(JsonableBaseEntity):

    def __init__(self, package_delivery_plans: List[PackageDeliveryPlan]):
        self._package_delivery_plans = package_delivery_plans

    @property
    def package_delivery_plans(self) -> [PackageDeliveryPlan]:
        return self._package_delivery_plans

    def calc_centroid(self) -> Point2D:
        return calc_centroid([pdp.drop_point for pdp in self._package_delivery_plans])

    def get_amount_of_package_type(self, package_type: PackageType) -> int:
        package_delivery_plans = self.package_delivery_plans
        return len(list(filter(lambda x: x.package_type == package_type, package_delivery_plans)))

    def __eq__(self, other):
        return self.package_delivery_plans == other.package_delivery_plans

    def __hash__(self):
        return hash(tuple(self.package_delivery_plans))

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return CustomerDelivery(
            package_delivery_plans=[PackageDeliveryPlan.dict_to_obj(pdp_dict) for pdp_dict in
                                    dict_input['package_delivery_plans']])


DEFAULT_PDP_DISTRIB = PackageDeliveryPlanDistribution(DEFAULT_DROP_POINT_DISTRIB,
                                                      DEFAULT_AZI_DISTRIB,
                                                      DEFAULT_PITCH_DISTRIB,
                                                      DEFAULT_PACKAGE_DISTRIB)


class CustomerDeliveryDistribution(Distribution):
    def __init__(self, package_delivery_plan_distributions=None):
        if package_delivery_plan_distributions is None:
            package_delivery_plan_distributions = [DEFAULT_PDP_DISTRIB]
        self._pdp_distributions = package_delivery_plan_distributions

    def choose_rand(self, random: Random, amount: int = 1, num_pdp: int = 1) -> List[CustomerDelivery]:
        pdp_distributions = UniformChoiceDistribution(self._pdp_distributions).choose_rand(random, amount=amount)
        return [CustomerDelivery(pdp_distributions[i].choose_rand(random, amount=num_pdp)) for i in list(range(amount))]
