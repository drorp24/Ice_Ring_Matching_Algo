from __future__ import annotations
from datetime import datetime, date, time
from typing import Dict

from time_window import TimeWindow

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
