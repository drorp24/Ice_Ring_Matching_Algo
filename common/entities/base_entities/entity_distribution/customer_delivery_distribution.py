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
from geometry.geo_factory import create_zero_point_2d

DEFAULT_PDP_DISTRIB = PackageDeliveryPlanDistribution(relative_location_distribution=DEFAULT_RELATIVE_DROP_DISTRIB,
                                                      azimuth_distribution=DEFAULT_AZI_DISTRIB,
                                                      pitch_distribution=DEFAULT_PITCH_DISTRIB,
                                                      package_type_distribution=DEFAULT_PACKAGE_DISTRIB)


class CustomerDeliveryDistribution(HierarchialDistribution):

    def __init__(self, relative_location_distribution: PointLocationDistribution = DEFAULT_RELATIVE_DROP_DISTRIB,
                 package_delivery_plan_distributions: [PackageDeliveryPlanDistribution] = [DEFAULT_PDP_DISTRIB]):
        self._relative_location_distribution = relative_location_distribution
        self._pdp_distributions = package_delivery_plan_distributions

    def choose_rand(self, random: Random, base_loc: Point2D = create_zero_point_2d(), amount: Dict[type, int] = {}) -> List[CustomerDelivery]:
        internal_amount = LocalDistribution.get_updated_internal_amount(CustomerDeliveryDistribution, amount)
        cd_amount = internal_amount.pop(CustomerDelivery)
        sampled_distributions = self._calc_samples_from_distributions(cd_amount, random)
        CustomerDeliveryDistribution._update_the_location_of_sampled_points(base_loc, sampled_distributions)
        pdp_distribution = self.choose_internal_distribution(random)
        '''TODO: calculate single package delivery type for each pdp entity_distribution in customer delivery
        This means that the package_delivery_type might need to be an attribute of Customer Delivery'''
        return CustomerDeliveryDistribution._calc_result_list(internal_amount, pdp_distribution, random, sampled_distributions)

    def choose_internal_distribution(self, random):
        return UniformChoiceDistribution(self._pdp_distributions).choose_rand(random=random, amount=1)[0]

    @staticmethod
    def _update_the_location_of_sampled_points(base_loc: Point2D, sampled_distributions: Dict):
        sampled_distributions['location'] = LocalDistribution.add_base_point_to_relative_points(
            relative_points=sampled_distributions['location'], base_point=base_loc)

    def _calc_samples_from_distributions(self, cd_amount: int, random: Random) -> Dict[str, list]:
        return LocalDistribution.choose_rand_by_attrib(
            internal_sample_dict={'location': self._relative_location_distribution},
            random=random,
            amount=cd_amount)

    @staticmethod
    def _calc_result_list(internal_amount: Dict[type, int], pdp_distribution: PackageDeliveryPlanDistribution,
                          random: Random, sampled_distributions: Dict[str, list]) -> List[CustomerDelivery]:
        return [CustomerDelivery(
            pdp_distribution.choose_rand(random=random, amount=internal_amount[PackageDeliveryPlan], base_loc=loc))
            for loc in sampled_distributions['location']]

    @staticmethod
    def get_base_amount() -> Dict[type, int]:
        return {CustomerDelivery: 1, PackageDeliveryPlan: 1}
