import math
from enum import Enum, auto
from abc import ABC


class _AngleName(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self


class _AngleUnit(_AngleName):
    DEGREE = auto()
    RADIAN = auto()


class Angle(ABC):

    @property
    def radians(self) -> float:
        raise NotImplementedError()

    @property
    def degrees(self) -> float:
        raise NotImplementedError()


class _Angle(Angle):

    def __init__(self, value: float, unit: _AngleUnit):
        if unit == _AngleUnit.RADIAN:
            self._degrees = math.degrees(value)
            self._radians = value
        else:
            self._degrees = value
            self._radians = math.radians(value)
        self._unit = unit

    @property
    def radians(self) -> float:
        return self._radians

    @property
    def degrees(self) -> float:
        return self._degrees


def create_degree_angle(value: float) -> Angle:
    return _Angle(value, unit=_AngleUnit.DEGREE)


def create_radian_angle(value: float) -> Angle:
    return _Angle(value, unit=_AngleUnit.RADIAN)
