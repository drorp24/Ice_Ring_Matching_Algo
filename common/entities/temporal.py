from __future__ import annotations

from datetime import datetime, date, time, timedelta
from random import Random
from typing import Dict, List

from time_window import TimeWindow

from common.entities.base_entities.distribution import Distribution, UniformChoiceDistribution

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


class TimeWindowExtension:

    def __init__(self, since: DateTimeExtension, until: DateTimeExtension):
        self._time_window = TimeWindow(since.internal_date_time, until.internal_date_time)

    @property
    def internal_time_window(self) -> TimeWindow:
        return self._time_window

    def to_dict(self) -> dict:
        since = {SINCE: DateTimeExtension.from_dt(self.internal_time_window.since).to_dict()}
        until = {UNTIL: DateTimeExtension.from_dt(self.internal_time_window.until).to_dict()}
        return {**since, **until}

    @staticmethod
    def from_dict(time_window_dict: Dict) -> TimeWindowExtension:
        since = DateTimeExtension.from_dict(time_window_dict[SINCE])
        until = DateTimeExtension.from_dict(time_window_dict[UNTIL])
        return TimeWindowExtension(since, until)

    def __eq__(self, other: TimeWindowExtension):
        return self.internal_time_window.since == other.internal_time_window.since and \
               self.internal_time_window.until == other.internal_time_window.until


class DateTimeExtension:

    def __init__(self, dt_date: date = date(2000, 1, 1), dt_time: time = time(6, 0, 0)):
        self._date_time: datetime = datetime(year=dt_date.year, month=dt_date.month, day=dt_date.day, hour=dt_time.hour,
                                             minute=dt_time.minute, second=dt_time.second)

    @classmethod
    def from_dt(cls, date_time: datetime) -> DateTimeExtension:
        return DateTimeExtension(date_time.date(), date_time.time())

    @property
    def internal_date_time(self) -> datetime:
        return self._date_time

    def to_dict(self) -> Dict:
        date_dict = DateTimeExtension.extract_date_dict_from_datetime(self.internal_date_time)
        time_dict = DateTimeExtension.extract_time_dict_from_datetime(self.internal_date_time)
        return {**date_dict, **time_dict}

    @staticmethod
    def from_dict(date_time_dict: Dict) -> DateTimeExtension:
        date_instance = DateTimeExtension.extract_date_from_datetime_dict(date_time_dict)
        time_instance = DateTimeExtension.extract_time_from_datetime_dict(date_time_dict)
        return DateTimeExtension(date_instance, time_instance)

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
        return DateTimeExtension(self.internal_date_time + time_delta.internal_delta)

    def __eq__(self, other: DateTimeExtension):
        return self.internal_date_time == other.internal_date_time

    def __gt__(self, other: DateTimeExtension):
        return self.internal_date_time > other.internal_date_time


class TimeDeltaExtension:
    
    def __init__(self, time_delta: timedelta = timedelta(hours=1)):
        self._time_delta: timedelta = time_delta

    @property
    def internal_delta(self) -> timedelta:
        return self._time_delta

    def __eq__(self, other: TimeDeltaExtension):
        return self.internal_delta == other.internal_delta
    

_DEFAULT_DATE_TIME_MORNING = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))
_DEFAULT_DATE_MID_DAY = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(12, 30, 0))
_DEFAULT_DATE_TIME_NIGHT = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(23, 59, 0))

_DEFAULT_TIME_DELTA_OPTIONS = [timedelta(hours=3), timedelta(minutes=30), timedelta(hours=2, minutes=20)]

_DEFAULT_DT_OPTIONS = [_DEFAULT_DATE_TIME_MORNING, _DEFAULT_DATE_MID_DAY, _DEFAULT_DATE_TIME_NIGHT]

_DEFAULT_TIME_WINDOW = TimeWindowExtension(_DEFAULT_DATE_TIME_MORNING, _DEFAULT_DATE_TIME_NIGHT)


class DateTimeDistribution(UniformChoiceDistribution):
    def __init__(self, date_time_options: List[DateTimeExtension] = _DEFAULT_DT_OPTIONS):
        super().__init__(date_time_options)


class TimeDeltaDistribution(UniformChoiceDistribution):
    def __init__(self, time_delta_list: List[timedelta]):
        super().__init__(time_delta_list)


class TimeWindowDistribution(Distribution):

    def __init__(self, start_time_distribution: DateTimeDistribution = DateTimeDistribution(_DEFAULT_DT_OPTIONS),
                 time_delta_distribution: TimeDeltaDistribution = TimeDeltaDistribution(_DEFAULT_TIME_DELTA_OPTIONS)):
        self._start_date_time_distribution = start_time_distribution
        self._time_delta_distribution = time_delta_distribution

    def choose_rand(self, random: Random, num_to_choose: int = 1):
        start_times: List[DateTimeExtension] = self._start_date_time_distribution.choose_rand(random, num_to_choose)
        deltas: List[TimeDeltaExtension] = self._time_delta_distribution.choose_rand(random, num_to_choose)
        return [TimeWindowExtension(start_time, start_time.add_time_delta(delta)) for (start_time, delta) in
                zip(start_times, deltas)]


class NoViableTimesGivenDistribution(Exception):
    pass
