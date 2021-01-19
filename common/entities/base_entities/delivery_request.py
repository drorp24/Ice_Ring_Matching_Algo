from __future__ import annotations

from datetime import date, time, timedelta

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    DateTimeDistribution, TimeWindowDistribution
from common.entities.base_entities.temporal import TimeWindowExtension, Temporal, DateTimeExtension, TimeDeltaExtension
from geometry.geo2d import Point2D
from geometry.geo_factory import calc_centroid
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

    def __eq__(self, other: DeliveryRequest):
        return (self.__class__ == other.__class__) and \
               (self.delivery_options == other.delivery_options) and \
               (self.time_window == other.time_window) and \
               (self.priority == other.priority)

    def __hash__(self):
        return hash((tuple(self.delivery_options), self.time_window, self.priority))


def create_default_time_window_for_delivery_request():
    default_date_time_morning = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))
    default_date_time_night = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(23, 59, 0))
    default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3)),
                                                        TimeDeltaExtension(timedelta(minutes=30))])
    default_dt_options = [default_date_time_morning, default_date_time_night]
    return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)
