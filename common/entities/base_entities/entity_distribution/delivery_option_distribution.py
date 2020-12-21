from abc import ABCMeta
from random import Random
from typing import List, Dict

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution, DEFAULT_PDP_DISTRIB
from common.entities.base_entities.entity_distribution.distribution_utils import LocalDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import UniformChoiceDistribution, HierarchialDistribution
from geometry.distribution.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

DEFAULT_CD_DISTRIB = CustomerDeliveryDistribution(package_delivery_plan_distributions=[DEFAULT_PDP_DISTRIB])


class DeliveryOptionDistribution(HierarchialDistribution):
    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 customer_delivery_distributions: List[CustomerDeliveryDistribution] = DEFAULT_CD_DISTRIB):
        self._relative_location_distribution = relative_location_distribution
        self._customer_delivery_distributions = customer_delivery_distributions

    def choose_rand(self, random: Random, base_loc: Point2D = create_point_2d(0, 0),
                    amount: Dict[type, int] = {}) -> List[DeliveryOption]:
        internal_amount = DeliveryOptionDistribution.get_base_amount()
        internal_amount.update(amount)
        cd_distributions = UniformChoiceDistribution(self._customer_delivery_distributions).choose_rand(random, 1)[0]
        relative_locations = LocalDistribution.add_base_point_to_relative_points(
            relative_points=self._relative_location_distribution.choose_rand(random, internal_amount[DeliveryOption]),
            base_point=base_loc)
        internal_amount.pop(DeliveryOption)
        return [DeliveryOption(
            cd_distributions.choose_rand(random=random, base_loc=loc, amount=internal_amount))
            for loc in relative_locations]

    @staticmethod
    def get_base_amount():
        return {DeliveryOption: 1, CustomerDelivery: 1, PackageDeliveryPlan: 1}
