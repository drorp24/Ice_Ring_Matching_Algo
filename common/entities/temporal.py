from __future__ import annotations

from datetime import datetime, date, time, timedelta
from random import Random
from typing import Dict, List, Union

from time_window import TimeWindow

from common.entities.disribution.distribution import Distribution, UniformChoiceDistribution
from common.entities.base_entity import BaseEntity, JsonableBaseEntity

DATE = 'date'
TIME = 'time'
YEAR = 'year'
MONTH = 'month'
DAY = 'day'
HOUR = 'hour'
MINUTE = 'minute'
SECOND = 'second'
SINCE = 'since'
UNTIL = 'until'


class TimeWindowExtension(JsonableBaseEntity):

    def __init__(self, since: DateTimeExtension, until: DateTimeExtension):
        self._time_window = TimeWindow(tm_since=since._internal, tm_until=until._internal)

    @property
    def _internal(self) -> TimeWindow:
        return self._time_window

    @property
    def since(self) -> DateTimeExtension:
        return DateTimeExtension.from_dt(self._internal.since)

    @property
    def until(self) -> DateTimeExtension:
        return DateTimeExtension.from_dt(self._internal.until)

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        since = DateTimeExtension.from_dict(dict_input[SINCE])
        until = DateTimeExtension.from_dict(dict_input[UNTIL])
        return TimeWindowExtension(since, until)

    def __eq__(self, other: TimeWindowExtension):
        return self._internal.since == other._internal.since and \
               self._internal.until == other._internal.until

    def __hash__(self):
        return hash(self._internal)

    def __contains__(self, temporal: Union[DateTimeExtension, TimeWindowExtension]):
        try:
            return temporal._internal in self._internal
        except:
            return temporal.since._internal in self._internal and temporal.until._internal in self._internal


class DateTimeExtension(BaseEntity):

    def __init__(self, dt_date: date, dt_time: time):
        self._date_time: datetime = datetime(year=dt_date.year, month=dt_date.month, day=dt_date.day, hour=dt_time.hour,
                                             minute=dt_time.minute, second=dt_time.second)

    @classmethod
    def from_dt(cls, date_time: datetime) -> DateTimeExtension:
        return DateTimeExtension(date_time.date(), date_time.time())

    @property
    def _internal(self) -> datetime:
        return self._date_time

    @property
    def date(self) -> date:
        return self._date_time.date()

    @property
    def time(self) -> date:
        return self._date_time.time()

    def __dict__(self):
        val = self.to_dict()
        val.update({'__class__': self.__class__.__name__})
        return val

    def __hash__(self):
        return hash(self._internal)

    def to_dict(self) -> Dict:
        date_dict = DateTimeExtension.extract_date_dict_from_datetime(self._internal)
        time_dict = DateTimeExtension.extract_time_dict_from_datetime(self._internal)
        return {**date_dict, **time_dict}

    @staticmethod
    def from_dict(date_time_dict: Dict) -> DateTimeExtension:
        date_instance = DateTimeExtension.extract_date_from_datetime_dict(date_time_dict)
        time_instance = DateTimeExtension.extract_time_from_datetime_dict(date_time_dict)
        return DateTimeExtension(dt_date=date_instance, dt_time=time_instance)

    @staticmethod
    def extract_date_from_datetime_dict(date_time_dict: Dict) -> date:
        date_dict = date_time_dict[DATE]
        date_instance = date(date_dict[YEAR], date_dict[MONTH], date_dict[DAY])
        return date_instance

    @staticmethod
    def extract_time_from_datetime_dict(date_time_dict: Dict) -> time:
        time_dict = date_time_dict[TIME]
        time_instance = time(time_dict[HOUR], time_dict[MINUTE], time_dict[SECOND])
        return time_instance

    @staticmethod
    def extract_date_dict_from_datetime(date_time: datetime) -> Dict:
        return {DATE: {YEAR: date_time.year, MONTH: date_time.month, DAY: date_time.day}}

    @staticmethod
    def extract_time_dict_from_datetime(date_time: datetime) -> Dict:
        return {TIME: {HOUR: date_time.hour, MINUTE: date_time.minute, SECOND: date_time.second}}

    def add_time_delta(self, time_delta: TimeDeltaExtension) -> DateTimeExtension:
        return DateTimeExtension.from_dt(self._internal + time_delta._internal)

    def __eq__(self, other: DateTimeExtension):
        return self._internal == other._internal

    def __gt__(self, other: DateTimeExtension):
        return self._internal > other._internal


class TimeDeltaExtension(BaseEntity):

    def __init__(self, time_delta: timedelta = timedelta(hours=1)):
        self._time_delta: timedelta = time_delta

    @property
    def _internal(self) -> timedelta:
        return self._time_delta

    def __eq__(self, other: TimeDeltaExtension):
        return self._internal.seconds == other._internal.seconds

    def __repr__(self):
        return self._internal.__repr__()

    def __hash__(self):
        return hash(self._internal)


class DateTimeDistribution(UniformChoiceDistribution):
    def __init__(self, date_time_options: List[DateTimeExtension]):
        super().__init__(date_time_options)

    def choose_rand(self, random: Random, amount: int = 1) -> List[DateTimeExtension]:
        return super().choose_rand(random, amount)


class TimeDeltaDistribution(UniformChoiceDistribution):
    def __init__(self, time_delta_list: List[TimeDeltaExtension]):
        super().__init__(time_delta_list)

    def choose_rand(self, random: Random, amount: int = 1) -> List[TimeDeltaExtension]:
        return super().choose_rand(random, amount)


class TimeWindowDistribution(Distribution):

    def __init__(self, start_time_distribution: DateTimeDistribution,
                 time_delta_distribution: TimeDeltaDistribution):
        self._start_date_time_distribution = start_time_distribution
        self._time_delta_distribution = time_delta_distribution

    def choose_rand(self, random: Random, amount: int = 1) -> List[TimeWindowExtension]:
        start_times: List[DateTimeExtension] = self._start_date_time_distribution.choose_rand(random, amount)
        deltas: List[TimeDeltaExtension] = self._time_delta_distribution.choose_rand(random, amount)
        return [TimeWindowExtension(start_time, start_time.add_time_delta(delta)) for (start_time, delta) in
                zip(start_times, deltas)]


class NoViableTimesGivenDistribution(Exception):
    pass
