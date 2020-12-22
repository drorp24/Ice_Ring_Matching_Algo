import math
from random import Random
from typing import List, Dict, Union

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution, DEFAULT_PDP_DISTRIB
from common.entities.base_entities.entity_distribution.distribution_utils import DistributionUtils
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import UniformChoiceDistribution, HierarchialDistribution, Range, \
    UniformDistribution
from geometry.distribution.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_zero_point_2d

DEFAULT_CD_DISTRIB = CustomerDeliveryDistribution(package_delivery_plan_distributions=[DEFAULT_PDP_DISTRIB])


class DeliveryOptionDistribution(HierarchialDistribution):
    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 customer_delivery_distributions: List[CustomerDeliveryDistribution] = DEFAULT_CD_DISTRIB):
        self._relative_location_distribution = relative_location_distribution
        self._customer_delivery_distributions = customer_delivery_distributions

    def choose_rand(self, random: Random, base_loc: Point2D = create_zero_point_2d(),
                    amount: Dict[type, Union[int, Range]] = {}) -> List[DeliveryOption]:
        internal_amount = DistributionUtils.get_updated_internal_amount(DeliveryOptionDistribution, amount)
        do_amount = DistributionUtils.extract_amount_in_range(internal_amount.pop(DeliveryOption), random)
        sampled_distributions = self._calc_samples_from_distributions(do_amount, random)
        DeliveryOptionDistribution._update_location_of_sampled_points(base_loc, sampled_distributions)
        cd_distributions = self.choose_internal_distribution(random)
        return DeliveryOptionDistribution._calc_result_list(cd_distributions, internal_amount, random, sampled_distributions)

    def choose_internal_distribution(self, random):
        return UniformChoiceDistribution(self._customer_delivery_distributions).choose_rand(random, 1)[0]

    def _calc_samples_from_distributions(self, do_amount: int, random: Random) -> Dict[str, list]:
        return DistributionUtils.choose_rand_by_attrib(
            internal_sample_dict={'location': self._relative_location_distribution},
            random=random,
            amount=do_amount)

    @staticmethod
    def _update_location_of_sampled_points(base_loc: Point2D, sampled_distributions: Dict):
        sampled_distributions['location'] = DistributionUtils.add_base_point_to_relative_points(
            relative_points=sampled_distributions['location'], base_point=base_loc)

    @staticmethod
    def _calc_result_list(cd_distributions, internal_amount, random, sampled_distributions) -> List[DeliveryOption]:
        return [DeliveryOption(cd_distributions.choose_rand(random=random, base_loc=loc, amount=internal_amount))
                for loc in sampled_distributions['location']]

    @staticmethod
    def get_base_amount() -> Dict[type, int]:
        return {DeliveryOption: 1, CustomerDelivery: 1, PackageDeliveryPlan: 1}
