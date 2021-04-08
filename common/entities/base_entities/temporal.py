from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, date, time, timedelta
from typing import Dict, Union, Tuple

from time_window import TimeWindow

from common.entities.base_entities.base_entity import JsonableBaseEntity, BaseEntity

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

SEC_IN_MIN = 60
MIN_IN_HOUR = 60

DATETIME_DEFAULT_FORMAT = "%d/%m/%Y %H:%M:%S"


class Temporal(ABC):

    @property
    @abstractmethod
    def time_window(self):
        raise NotImplementedError()


class TimeWindowExtension(JsonableBaseEntity):

    def __init__(self, since: DateTimeExtension, until: DateTimeExtension):
        self._time_window = TimeWindow(tm_since=since.get_internal(), tm_until=until.get_internal())

    def get_internal(self) -> TimeWindow:
        return self._time_window

    @property
    def since(self) -> DateTimeExtension:
        return DateTimeExtension.from_dt(self.get_internal().since)

    @property
    def until(self) -> DateTimeExtension:
        return DateTimeExtension.from_dt(self.get_internal().until)

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        since = DateTimeExtension.from_dict(dict_input[SINCE])
        until = DateTimeExtension.from_dict(dict_input[UNTIL])
        return TimeWindowExtension(since, until)

    def get_time_stamp(self) -> Tuple[int, int]:
        return self.get_internal().since.timestamp(), self.get_internal().until.timestamp()

    def overlaps(self, other: TimeWindowExtension) -> bool:
        return self.get_internal().overlaps(other.get_internal())
        # return int(self._internal.since.timestamp()), int(self._internal.until.timestamp())

    def get_relative_time_in_min(self, zero_time: DateTimeExtension) -> (float, float):
        return self.since.get_time_delta(zero_time).in_minutes(), self.until.get_time_delta(zero_time).in_minutes()

    def __eq__(self, other: TimeWindowExtension):
        return self.get_internal().since == other.get_internal().since and \
               self.get_internal().until == other.get_internal().until

    def __hash__(self):
        return hash(self.get_internal())

    def __contains__(self, temporal: Union[DateTimeExtension, TimeWindowExtension]):
        return temporal.get_internal() in self.get_internal()


class DateTimeExtension(BaseEntity):

    def __init__(self, dt_date: date, dt_time: time):
        self._date_time: datetime = datetime(year=dt_date.year, month=dt_date.month, day=dt_date.day, hour=dt_time.hour,
                                             minute=dt_time.minute, second=dt_time.second)

    @classmethod
    def from_dt(cls, date_time: datetime) -> DateTimeExtension:
        return DateTimeExtension(date_time.date(), date_time.time())

    @classmethod
    def extract_time_from_iso(cls, date_time: str) -> DateTimeExtension:
        date_time = datetime.fromisoformat(date_time)
        return DateTimeExtension.from_dict({DATE: {YEAR: date_time.year, MONTH: date_time.month, DAY: date_time.day},
                                            TIME: {HOUR: date_time.hour, MINUTE: date_time.minute,
                                                   SECOND: date_time.second}})

    def get_internal(self) -> datetime:
        return self._date_time

    @property
    def date(self) -> date:
        return self._date_time.date()

    @property
    def time(self) -> date:
        return self._date_time.time()

    def time_stamp(self) -> float:
        return self._date_time.timestamp()

    def __dict__(self):
        val = self.to_dict()
        val.update({'__class__': self.__class__.__name__})
        return val

    def __hash__(self):
        return self.get_internal().__hash__()

    def to_dict(self) -> Dict:
        date_dict = DateTimeExtension.extract_date_dict_from_datetime(self.get_internal())
        time_dict = DateTimeExtension.extract_time_dict_from_datetime(self.get_internal())
        return {**date_dict, **time_dict}

    def str_format_time(self, fmt: str = DATETIME_DEFAULT_FORMAT) -> str:
        return self._date_time.strftime(fmt)

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
        return DateTimeExtension.from_dt(self.get_internal() + time_delta.get_internal())

    def get_time_delta(self, from_time: DateTimeExtension) -> TimeDeltaExtension:
        return TimeDeltaExtension(self.get_internal() - from_time.get_internal())

    def __eq__(self, other: DateTimeExtension):
        return self.get_internal() == other.get_internal()

    def __gt__(self, other: DateTimeExtension):
        return self.get_internal() > other.get_internal()


class TimeDeltaExtension(BaseEntity):

    def __init__(self, time_delta: timedelta = timedelta(hours=1)):
        self._time_delta: timedelta = time_delta

    def get_internal(self) -> timedelta:
        return self._time_delta

    def __eq__(self, other: TimeDeltaExtension):
        return self.get_internal().seconds == other.get_internal().seconds

    def __repr__(self):
        return self.get_internal().__repr__()

    def __hash__(self):
        return hash(self.get_internal())

    def in_minutes(self) -> float:
        return self.get_internal().total_seconds() / SEC_IN_MIN


def current_milli_time() -> int:
    return int(round(time.time() * 1000))


class NoViableTimesGivenDistribution(Exception):
    pass
