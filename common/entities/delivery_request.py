from random import Random
from typing import List

from time_window import TimeWindow

from common.entities.base_entities.distribution import UniformChoiceDistribution
from common.entities.delivery_option import DeliveryOption, DeliveryOptionDistribution
from common.entities.temporal import TimeWindowDistribution, DateTimeDistribution


class DeliveryRequest:

    def __init__(self, delivery_options: [DeliveryOption], time_window: TimeWindow, priority: int):
        self._delivery_options = delivery_options if delivery_options is not None else []
        self._time_window = time_window
        self._priority = priority

    def __eq__(self, other):
        return (self.delivery_options == other.delivery_options) and \
               (self.time_window == other.time_window) and \
               (self.priority == other.priority)

    @property
    def delivery_options(self) -> [DeliveryOption]:
        return self._delivery_options

    @property
    def time_window(self) -> TimeWindow:
        return self._time_window

    @property
    def priority(self) -> int:
        return self._priority


_DEFAULT_DR_DISTRIB = [DeliveryOptionDistribution()]

_DEFAULT_TW_DISTRIB = TimeWindowDistribution()


class DeliveryRequestDistribution(UniformChoiceDistribution):
    def __init__(self, delivery_option_distributions: List[DeliveryOptionDistribution] = _DEFAULT_DR_DISTRIB,
                 time_window_distrib: TimeWindowDistribution = TimeWindowDistribution()):
        super().__init__(delivery_option_distributions)

    def choose_rand(self, random: Random, num_to_choose: int = 1, num_od: int = 1, num_cd: int = 1, num_pdp: int = 1) -> \
            List[DeliveryRequest]:
        delivery_request_distributions = super().choose_rand(random, num_to_choose)
        return [DeliveryRequest(distrib.choose_rand(random, num_od, num_cd, num_pdp),) for distrib in
                delivery_request_distributions]
