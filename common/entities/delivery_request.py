from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta, time, date
from random import Random
from typing import List

from common.entities.base_entity import JsonableBaseEntity
from common.entities.customer_delivery import CustomerDeliveryDistribution
from common.entities.delivery_option import DeliveryOption, DeliveryOptionDistribution, DEFAULT_CD_DISTRIB
from common.entities.disribution.distribution import UniformChoiceDistribution, Distribution
from common.entities.package import PackageDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution, \
    DEFAULT_PITCH_DISTRIB, DEFAULT_PACKAGE_DISTRIB, DEFAULT_AZI_DISTRIB
from common.entities.temporal import TimeWindowDistribution, TimeWindowExtension, DateTimeDistribution, \
    TimeDeltaExtension, TimeDeltaDistribution, DateTimeExtension, Temporal
from common.math.angle import AngleUniformDistribution
from geometry.geo2d import Point2D
from geometry.geo_distribution import PointLocationDistribution, UniformPointInBboxDistribution, \
    DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo_factory import calc_centroid, create_point_2d
from geometry.utils import Localizable


class DeliveryRequest(JsonableBaseEntity, Localizable, Temporal):

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

    def calc_location(self) -> Point2D:
        return calc_centroid([do.calc_location() for do in self.delivery_options])

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DeliveryRequest(
            delivery_options=[DeliveryOption.dict_to_obj(do_dict) for do_dict in dict_input['delivery_options']],
            time_window=TimeWindowExtension.dict_to_obj(dict_input['time_window']),
            priority=dict_input['priority']
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (self.delivery_options == other.delivery_options) and \
               (self.time_window == other.time_window) and \
               (self.priority == other.priority)

    def __hash__(self):
        return hash((tuple(self.delivery_options), self.time_window, self.priority))


class PriorityDistribution(UniformChoiceDistribution):
    def __init__(self, priorities: List[float]):
        super().__init__(priorities)


def create_default_time_window_for_delivery_request():
    default_date_time_morning = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))
    default_date_time_night = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(23, 59, 0))
    default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3)),
                                                        TimeDeltaExtension(timedelta(minutes=30))])
    default_dt_options = [default_date_time_morning, default_date_time_night]
    return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)


DEFAULT_DO_DISTRIB = DeliveryOptionDistribution(relative_location_distribution=DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                                                customer_delivery_distributions=[DEFAULT_CD_DISTRIB])

DEFAULT_TW_DISRIB = create_default_time_window_for_delivery_request()

DEFAULT_PRIORITY_DISTRIB = PriorityDistribution(list(range(0, 100, 3)))

DEFAULT_LOC_DISTRIB = UniformPointInBboxDistribution(0, 100, 0, 100)


class DeliveryRequestDistribution(Distribution):
    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_LOC_DISTRIB,
                 delivery_option_distributions: [DeliveryOptionDistribution] = [DEFAULT_DO_DISTRIB],
                 time_window_distributions: TimeWindowDistribution = DEFAULT_TW_DISRIB,
                 priority_distribution: PriorityDistribution = DEFAULT_PRIORITY_DISTRIB):
        self._relative_location_distribution = relative_location_distribution
        self._do_distribution_options = delivery_option_distributions
        self._time_window_distributions = time_window_distributions
        self._priority_distribution = priority_distribution

    def choose_rand(self, random: Random, base_location: Point2D = create_point_2d(0, 0),
                    amount: int = 1, num_do: int = 1, num_cd: int = 1, num_pdp: int = 1) -> List[DeliveryRequest]:
        relative_locations = self._relative_location_distribution.choose_rand(random, amount)
        do_distribution = UniformChoiceDistribution(self._do_distribution_options).choose_rand(random, 1)[0]
        time_window_distributions = self._time_window_distributions.choose_rand(random, amount)
        priority_distribution = self._priority_distribution.choose_rand(random, amount)
        return [DeliveryRequest(
            do_distribution.choose_rand(random=random, base_location=base_location + relative_locations[i],
                                        amount=num_do, num_cd=num_cd, num_pdp=num_pdp),
            time_window_distributions[i], priority_distribution[i]) for i in list(range(amount))]


def build_delivery_request_distribution(
        relative_dr_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        relative_do_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        relative_cd_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        relative_pdp_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        azimuth_distribution: AngleUniformDistribution = DEFAULT_AZI_DISTRIB,
        pitch_distribution: AngleUniformDistribution = DEFAULT_PITCH_DISTRIB,
        package_type_distribution: PackageDistribution = DEFAULT_PACKAGE_DISTRIB,
        priority_distribution: PriorityDistribution = DEFAULT_PRIORITY_DISTRIB,
        time_window_distribution: TimeWindowDistribution = DEFAULT_TW_DISRIB) -> DeliveryRequestDistribution:
    pdp_distributions = [PackageDeliveryPlanDistribution(
        relative_location_distribution=relative_pdp_location_distribution,
        azimuth_distribution=azimuth_distribution,
        pitch_distribution=pitch_distribution,
        package_type_distribution=package_type_distribution)]
    cd_distributions = [CustomerDeliveryDistribution(
        package_delivery_plan_distributions=pdp_distributions,
        relative_location_distribution=relative_cd_location_distribution)]
    do_distributions = [DeliveryOptionDistribution(
        customer_delivery_distributions=cd_distributions,
        relative_location_distribution=relative_do_location_distribution)]
    return DeliveryRequestDistribution(
        delivery_option_distributions=do_distributions,
        priority_distribution=priority_distribution,
        time_window_distributions=time_window_distribution,
        relative_location_distribution=relative_dr_location_distribution)
