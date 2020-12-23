from __future__ import annotations

from random import Random
from typing import List

from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension, TimeWindowExtension
from common.entities.distribution.distribution import Distribution, UniformChoiceDistribution


class DateTimeDistribution(UniformChoiceDistribution):
    def __init__(self, date_time_options: List[DateTimeExtension]):
        super().__init__(date_time_options)

    def choose_rand(self, random: Random, amount: int = 1) -> List[DateTimeExtension]:
        return super().choose_rand(random, amount)

    def distribution_class(self) -> type:
        return DateTimeExtension


class TimeDeltaDistribution(UniformChoiceDistribution):
    def __init__(self, time_delta_list: List[TimeDeltaExtension]):
        super().__init__(time_delta_list)

    def choose_rand(self, random: Random, amount: int = 1) -> List[TimeDeltaExtension]:
        return super().choose_rand(random, amount)

    def distribution_class(self) -> type:
        return TimeDeltaExtension


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

    def distribution_class(self) -> type:
        return TimeWindowExtension


class NoViableTimesGivenDistribution(Exception):
    pass
