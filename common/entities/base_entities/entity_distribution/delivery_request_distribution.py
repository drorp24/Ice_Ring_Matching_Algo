from __future__ import annotations

from abc import ABCMeta
from random import Random
from typing import List, Dict

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest, \
    create_default_time_window_for_delivery_request
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution, \
    DEFAULT_CD_DISTRIB
from common.entities.base_entities.entity_distribution.distribution_utils import LocalDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeWindowDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import UniformChoiceDistribution, HierarchialDistribution
from geometry.distribution.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

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

    def choose_rand(self, random: Random, base_location: Point2D = create_point_2d(0, 0),
                    amount: Dict[type, int] = {}) -> List[DeliveryRequest]:
        internal_amount = DeliveryRequestDistribution.get_base_amount()
        internal_amount.update(amount)
        dr_amount = internal_amount[DeliveryRequest]

        do_distribution = UniformChoiceDistribution(self._do_distribution_options).choose_rand(random, 1)[0]
        relative_locations = LocalDistribution.add_base_point_to_relative_points(
            relative_points=self._relative_location_distribution.choose_rand(random, dr_amount),
            base_point=base_location)
        time_window_samples = self._time_window_distributions.choose_rand(random, dr_amount)
        priority_samples = self._priority_distribution.choose_rand(random, dr_amount)

        internal_amount.pop(DeliveryRequest)
        return [DeliveryRequest(
            do_distribution.choose_rand(random=random, base_loc=loc, amount=internal_amount), tw,
            priority) for (loc, tw, priority) in zip(relative_locations, time_window_samples, priority_samples)]

    @staticmethod
    def get_base_amount():
        return {DeliveryRequest: 1, DeliveryOption: 1, CustomerDelivery: 1, PackageDeliveryPlan: 1}
