from __future__ import annotations

from random import Random
from typing import List, Dict, Union

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest, \
    create_default_time_window_for_delivery_request
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution, \
    DEFAULT_CD_DISTRIB
from common.entities.base_entities.entity_distribution.distribution_utils import add_base_point_to_relative_points, \
    get_updated_internal_amount, extract_amount_in_range, choose_rand_by_attrib, validate_amount_input
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeWindowDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import UniformChoiceDistribution, HierarchialDistribution, Range
from geometry.distribution.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_zero_point_2d

DEFAULT_TW_DR_DISRIB = create_default_time_window_for_delivery_request()

DEFAULT_DO_DISTRIB = DeliveryOptionDistribution(
    relative_location_distribution=DEFAULT_ZERO_LOCATION_DISTRIBUTION,
    customer_delivery_distributions=[DEFAULT_CD_DISTRIB])

DEFAULT_DR_PRIORITY_DISTRIB = PriorityDistribution(list(range(0, 100, 3)))


class DeliveryRequestDistribution(HierarchialDistribution):

    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 delivery_option_distributions: [DeliveryOptionDistribution] = [DEFAULT_DO_DISTRIB],
                 time_window_distributions: TimeWindowDistribution = DEFAULT_TW_DR_DISRIB,
                 priority_distribution: PriorityDistribution = DEFAULT_DR_PRIORITY_DISTRIB):
        self._relative_location_distribution = relative_location_distribution
        self._do_distribution_options = delivery_option_distributions
        self._time_window_distributions = time_window_distributions
        self._priority_distribution = priority_distribution

    def choose_rand(self, random: Random, base_loc: Point2D = create_zero_point_2d(),
                    amount: Dict[type, Union[int, Range]] = {}) -> List[DeliveryRequest]:
        validate_amount_input(self, amount)
        internal_amount = get_updated_internal_amount(DeliveryRequestDistribution, amount)
        dr_amount = extract_amount_in_range(internal_amount.pop(DeliveryRequest), random)
        sampled_distributions = self._calc_samples_from_distributions(dr_amount, random)
        DeliveryRequestDistribution._update_the_location_of_sampled_points(base_loc, sampled_distributions)
        do_distribution = self.choose_internal_distribution(random)
        return self._calc_result_list(do_distribution, internal_amount, random, sampled_distributions)

    @classmethod
    def distribution_class(cls) -> type:
        return DeliveryRequest

    def choose_internal_distribution(self, random):
        return UniformChoiceDistribution(self._do_distribution_options).choose_rand(random, 1)[0]

    def _calc_samples_from_distributions(self, dr_amount: int, random: Random):
        return choose_rand_by_attrib(
            internal_sample_dict={'location': self._relative_location_distribution,
                                  'time_window': self._time_window_distributions,
                                  'priority': self._priority_distribution},
            random=random,
            amount=dr_amount)

    @staticmethod
    def _update_the_location_of_sampled_points(base_loc: Point2D, sampled_distributions: Dict):
        sampled_distributions['location'] = add_base_point_to_relative_points(
            relative_points=sampled_distributions['location'], base_point=base_loc)

    @staticmethod
    def _calc_result_list(do_distribution, internal_amount, random, sampled_distributions):
        return [DeliveryRequest(EntityID.generate_uuid(),
                                do_distribution.choose_rand(random=random, base_loc=loc, amount=internal_amount), tw,
                                priority)
                for (loc, tw, priority) in zip(sampled_distributions['location'],
                                               sampled_distributions['time_window'],
                                               sampled_distributions['priority'])]

    @staticmethod
    def get_all_internal_types():
        return [DeliveryRequest, DeliveryOption, CustomerDelivery, PackageDeliveryPlan]
