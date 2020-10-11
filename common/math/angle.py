import math
from enum import Enum, auto


class _AngleName(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self


class AngleUnit(_AngleName):
    DEGREE = auto()
    RADIAN = auto()


class Angle:
    def __init__(self, value: float, unit: AngleUnit):
        self.__value = value
        self.__unit = unit

    @property
    def _value(self) -> float:
        return self.__value

    @property
    def _unit(self) -> AngleUnit:
        return self.__unit

    def in_degrees(self) -> float:
        return self._value if self._unit is AngleUnit.DEGREE else math.degrees(self._value)

    def in_radians(self) -> float:
        return self._value if self._unit is AngleUnit.RADIAN else math.radians(self._value)
