from pprint import pprint
from random import Random
from typing import List

from common.entities.base_entities.distribution import UniformChoiceDistribution, Distribution
from common.entities.base_entity import BaseEntity
from common.entities.delivery_option import DeliveryOption, DeliveryOptionDistribution
from common.entities.temporal import TimeWindowDistribution, TimeWindowExtension


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


_DEFAULT_DR_DISTRIB = UniformChoiceDistribution([DeliveryOptionDistribution()])

_DEFAULT_TW_DISTRIB = TimeWindowDistribution()

_DEFAULT_PRIORITY_OPTIONS = list(range(0, 100, 3))


class PriorityDistribution(UniformChoiceDistribution):
    def __init__(self):
        super().__init__(_DEFAULT_PRIORITY_OPTIONS)


_DEFAULT_PRIORITY_DISTRIB = PriorityDistribution()


class DeliveryRequestDistribution(Distribution):
    def __init__(self, delivery_option_distributions: UniformChoiceDistribution = _DEFAULT_DR_DISTRIB,
                 time_window_distributions: TimeWindowDistribution = _DEFAULT_TW_DISTRIB,
                 priority_distribution: PriorityDistribution = _DEFAULT_PRIORITY_DISTRIB):
        self._delivery_option_distribution_options = delivery_option_distributions
        self._time_window_distributions = time_window_distributions
        self._priority_distribution = priority_distribution

    def choose_rand(self, random: Random, num_to_choose: int = 1, num_do: int = 1, num_cd: int = 1, num_pdp: int = 1) -> \
            List[DeliveryRequest]:
        delivery_request_distributions = self._delivery_option_distribution_options.choose_rand(random, num_to_choose)
        time_window = self._time_window_distributions.choose_rand(random, num_to_choose)
        priority_distribution = self._priority_distribution.choose_rand(random, num_to_choose)
        return [DeliveryRequest(
            distrib.choose_rand(random=random, num_cd=num_cd, num_pdp=num_pdp, num_to_choose=num_do),
            time_window[i],
            priority_distribution[i])
            for i, distrib in enumerate(delivery_request_distributions)]


if __name__ == '__main__':
    pprint(DeliveryRequestDistribution().choose_rand(Random(), 100))
