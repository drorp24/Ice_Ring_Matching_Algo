from random import Random
from typing import List

from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution, DEFAULT_PDP_DISTRIB
from common.entities.base_entities.entity_distribution.distribution_utils import LocalDistribution
from common.entities.distribution.distribution import UniformChoiceDistribution, Distribution
from geometry.distribution.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

DEFAULT_CD_DISTRIB = CustomerDeliveryDistribution(package_delivery_plan_distributions=[DEFAULT_PDP_DISTRIB])


class DeliveryOptionDistribution(Distribution):
    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 customer_delivery_distributions: List[CustomerDeliveryDistribution] = DEFAULT_CD_DISTRIB):
        self._relative_location_distribution = relative_location_distribution
        self._customer_delivery_distributions = customer_delivery_distributions

    def choose_rand(self, random: Random, base_loc: Point2D = create_point_2d(0, 0),
                    amount: int = 1, num_cd: int = 1, num_pdp: int = 1) -> List[DeliveryOption]:
        relative_locations = LocalDistribution.add_base_point_to_relative_points(
            relative_points=self._relative_location_distribution.choose_rand(random, amount),
            base_point=base_loc)
        cd_distributions = UniformChoiceDistribution(self._customer_delivery_distributions).choose_rand(random, 1)[0]
        return [DeliveryOption(
            cd_distributions.choose_rand(random=random, base_loc=loc, amount=num_cd, num_pdp=num_pdp))
            for loc in relative_locations]
