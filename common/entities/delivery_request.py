from __future__ import annotations

from random import Random
from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution, Distribution
from common.entities.base_entity import BaseEntity
from common.entities.customer_delivery import CustomerDeliveryDistribution
from common.entities.delivery_option import DeliveryOption, DeliveryOptionDistribution
from common.entities.package import PackageDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution
from common.entities.temporal import TimeWindowDistribution, TimeWindowExtension
from common.math.angle import AngleUniformDistribution
from geometry.geo_distribution import PointDistribution


class DeliveryRequest(BaseEntity):

    def __init__(self, delivery_options: [DeliveryOption], time_window: TimeWindowExtension, priority: int):
        self._delivery_options = delivery_options if delivery_options is not None else []
        self._time_window = time_window
        self._priority = priority

    @property
    def delivery_options(self) -> [DeliveryOption]:
        return self._delivery_options

    @property
    def time_window(self) -> TimeWindowExtension:
        return self._time_window

    @property
    def priority(self) -> int:
        return self._priority

    def __eq__(self, other):
        return (self.delivery_options == other.delivery_options) and \
               (self.time_window == other.time_window) and \
               (self.priority == other.priority)


class PriorityDistribution(UniformChoiceDistribution):
    def __init__(self, priorities: List[float]):
        super().__init__(priorities)


class DeliveryRequestDistribution(Distribution):
    def __init__(self, delivery_option_distributions: [DeliveryOptionDistribution],
                 time_window_distributions: TimeWindowDistribution,
                 priority_distribution: PriorityDistribution):
        self._do_distribution_options = delivery_option_distributions
        self._time_window_distributions = time_window_distributions
        self._priority_distribution = priority_distribution

    def choose_rand(self, random: Random, amount: int = 1, num_do: int = 1, num_cd: int = 1, num_pdp: int = 1) -> \
            List[DeliveryRequest]:

        do_distributions = UniformChoiceDistribution(self._do_distribution_options).choose_rand(random, amount)
        time_window_distributions = self._time_window_distributions.choose_rand(random, amount)
        priority_distribution = self._priority_distribution.choose_rand(random, amount)

        return [DeliveryRequest(do_distributions[i].choose_rand(random=random, amount=num_do, num_cd=num_cd, num_pdp=num_pdp),
                                time_window_distributions[i], priority_distribution[i]) for i in range(amount)]


def generate_delivery_request_distribution(drop_point_distribution: PointDistribution,
                                           azimuth_distribution: AngleUniformDistribution,
                                           pitch_distribution: UniformChoiceDistribution,
                                           package_type_distribution: PackageDistribution,
                                           priority_distribution: PriorityDistribution,
                                           time_window_distribution: TimeWindowDistribution):
    pdp_distribution = PackageDeliveryPlanDistribution(drop_point_distribution=drop_point_distribution,
                                                       azimuth_distribution=azimuth_distribution,
                                                       pitch_distribution=pitch_distribution,
                                                       package_type_distribution=package_type_distribution)
    pdp_distribution = [pdp_distribution]
    cd_distribution = [CustomerDeliveryDistribution(pdp_distribution)]
    do_distribution = [DeliveryOptionDistribution(cd_distribution)]
    return DeliveryRequestDistribution(delivery_option_distributions=do_distribution,
                                       priority_distribution=priority_distribution,
                                       time_window_distributions=time_window_distribution)
