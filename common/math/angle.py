import math
from enum import IntEnum


class AngleUnit(IntEnum):

    DEGREE = 1
    RADIAN = 2


class Angle:

    def __init__(self, value: float, unit: AngleUnit = AngleUnit.DEGREE):
        self._value = value
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> AngleUnit:
        return self._unit

    def convert_to_radians(self):
        return math.radians(self._value)

    def convert_to_degrees(self):
        return math.degrees(self._value)

