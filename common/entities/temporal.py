from __future__ import annotations
from datetime import datetime, date, time
from random import Random
from typing import Dict, List

from time_window import TimeWindow

from common.entities.base_entities.distribution import ChoiceDistribution, Distribution

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

    def __eq__(self, other: DateTimeExtension):
        return self.internal_date_time == other.internal_date_time

    def __gt__(self, other: DateTimeExtension):
        return self.internal_date_time > other.internal_date_time


class DateTimeDistribution(ChoiceDistribution):
    def __init__(self, date_time_options: List[DateTimeExtension]):
        super().__init__(date_time_options)


class TimeWindowDistribution(Distribution):

    def __init__(self, start_time_distribution: DateTimeDistribution, end_time_distribution: DateTimeDistribution):
        self._start_time_distribution = start_time_distribution
        self._end_time_distribution = end_time_distribution

    def choose_rand(self, random: Random):
        start_time_selected = self._start_time_distribution.choose_rand(random)
        earliest_end_time = min(self._end_time_distribution.get_choices())
        start_time_options = self._start_time_distribution.get_choices()
        valid_start_times = list(filter(lambda start_time: start_time < earliest_end_time, start_time_options))
        end_time_options = self._end_time_distribution.get_choices()
        viable_end_time_list = list(filter(lambda e_t: e_t < start_time_selected, end_time_options))
        if not valid_start_times or not viable_end_time_list:
            raise NoViableTimesGivenDistribution
        end_time_selected = DateTimeDistribution(viable_end_time_list).choose_rand(random)
        return TimeWindowExtension(start_time_selected, end_time_selected)


class NoViableTimesGivenDistribution(Exception):
    pass
