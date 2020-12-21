from abc import ABCMeta
from random import Random
from typing import List, Dict

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.entity_distribution.distribution_utils import LocalDistribution
from common.entities.base_entities.entity_distribution.package_delivery_plan_distribution import \
    PackageDeliveryPlanDistribution, DEFAULT_AZI_DISTRIB, DEFAULT_PITCH_DISTRIB, DEFAULT_PACKAGE_DISTRIB, \
    DEFAULT_RELATIVE_DROP_DISTRIB
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import UniformChoiceDistribution, HierarchialDistribution
from geometry.distribution.geo_distribution import PointLocationDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

DEFAULT_PDP_DISTRIB = PackageDeliveryPlanDistribution(relative_location_distribution=DEFAULT_RELATIVE_DROP_DISTRIB,
                                                      azimuth_distribution=DEFAULT_AZI_DISTRIB,
                                                      pitch_distribution=DEFAULT_PITCH_DISTRIB,
                                                      package_type_distribution=DEFAULT_PACKAGE_DISTRIB)


class CustomerDeliveryDistribution(HierarchialDistribution):

    def __init__(self, relative_location_distribution: PointLocationDistribution = DEFAULT_RELATIVE_DROP_DISTRIB,
                 package_delivery_plan_distributions: [PackageDeliveryPlanDistribution] = [DEFAULT_PDP_DISTRIB]):
        self._relative_location_distribution = relative_location_distribution
        self._pdp_distributions = package_delivery_plan_distributions

    def choose_rand(self, random: Random, base_loc: Point2D = create_point_2d(0, 0),
                    amount: Dict[type, int] = {}) -> List[CustomerDelivery]:
        internal_amount = CustomerDeliveryDistribution.get_base_amount()
        internal_amount.update(amount)

        pdp_distribution = UniformChoiceDistribution(self._pdp_distributions).choose_rand(random=random, amount=1)[0]
        relative_locations = LocalDistribution.add_base_point_to_relative_points(
            relative_points=self._relative_location_distribution.choose_rand(random=random,
                                                                             amount=internal_amount[CustomerDelivery]),
            base_point=base_loc)
        '''TODO: calculate single package delivery type for each pdp entity_distribution in customer delivery
        This means that the package_delivery_type might need to be an attribute of Customer Delivery'''
        return [CustomerDelivery(
            pdp_distribution.choose_rand(random=random, amount=internal_amount[PackageDeliveryPlan], base_loc=loc))
            for loc in relative_locations]

    @staticmethod
    def get_base_amount():
        return {CustomerDelivery: 1, PackageDeliveryPlan: 1}
