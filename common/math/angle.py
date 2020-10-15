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

    def __eq__(self, other):
        return self.in_degrees() == other.in_degrees()

    def in_degrees(self) -> float:
        return self.__value if self.__unit is AngleUnit.DEGREE else math.degrees(self.__value)

    def in_radians(self) -> float:
        return self.__value if self.__unit is AngleUnit.RADIAN else math.radians(self.__value)
