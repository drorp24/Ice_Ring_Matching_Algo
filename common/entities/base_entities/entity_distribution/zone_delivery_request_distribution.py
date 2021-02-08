from __future__ import annotations

from random import Random
from typing import List, Dict, Union

from common.entities.base_entities.delivery_request import DeliveryRequest, \
    create_default_time_window_for_delivery_request
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution, \
    DEFAULT_CD_DISTRIB
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeWindowDistribution
from common.entities.base_entities.zone import Zone
from common.entities.distribution.distribution import Range
from geometry.distribution.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_zero_point_2d

DEFAULT_TW_DR_DISRIB = create_default_time_window_for_delivery_request()

DEFAULT_DO_DISTRIB = DeliveryOptionDistribution(
    relative_location_distribution=DEFAULT_ZERO_LOCATION_DISTRIBUTION,
    customer_delivery_distributions=[DEFAULT_CD_DISTRIB])

DEFAULT_DR_PRIORITY_DISTRIB = PriorityDistribution(list(range(0, 100, 3)))


class ZoneDeliveryRequestDistribution(DeliveryRequestDistribution):

    def __init__(self, zones: List[Zone],
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 delivery_option_distributions: [DeliveryOptionDistribution] = [DEFAULT_DO_DISTRIB],
                 time_window_distributions: TimeWindowDistribution = DEFAULT_TW_DR_DISRIB,
                 priority_distribution: PriorityDistribution = DEFAULT_DR_PRIORITY_DISTRIB):
        super().__init__(relative_location_distribution,
                         delivery_option_distributions,
                         time_window_distributions,
                         priority_distribution)
        self._zones = zones

    @classmethod
    def create_from_base_class(cls, zones: List[Zone], delivery_request_distribution: DeliveryRequestDistribution):
        return ZoneDeliveryRequestDistribution(
            zones,
            relative_location_distribution=delivery_request_distribution._relative_location_distribution,
            delivery_option_distributions=delivery_request_distribution._do_distribution_options,
            time_window_distributions=delivery_request_distribution._time_window_distributions,
            priority_distribution=delivery_request_distribution._priority_distribution)

    @property
    def zones(self) -> List[Zone]:
        return self._zones

    def choose_rand(self, random: Random, base_loc: Point2D = create_zero_point_2d(),
                    amount: Dict[type, Union[int, Range]] = {}) -> List[DeliveryRequest]:
        return super().choose_rand(random=random, base_loc=base_loc, amount=amount)

    @classmethod
    def distribution_class(cls) -> type:
        return DeliveryRequest
