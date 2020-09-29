import math
from enum import IntEnum


class _AngleUnit(IntEnum):
    DEGREE = 1
    RADIAN = 2


class _Angle:

    def __init__(self, value: float, unit: _AngleUnit = _AngleUnit.DEGREE):
        self._value = value
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> _AngleUnit:
        return self._unit

    def convert_to_radians(self):
        if self._unit == _AngleUnit.RADIAN:
            return self._value
        return math.radians(self._value)

    def convert_to_degrees(self):
        if self._unit == _AngleUnit.DEGREE:
            return self._value
        return math.degrees(self._value)


def create_degree_angle(value: float) -> _Angle:
    return _Angle(value, unit=_AngleUnit.DEGREE)


def create_radian_angle(value: float) -> _Angle:
    return _Angle(value, unit=_AngleUnit.RADIAN)
