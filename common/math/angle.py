from __future__ import annotations
import math
from enum import Enum
from random import Random

from common.entities.base_entities.distribution import UniformDistribution, Range
from geometry.geo2d import Vector2D
from geometry.geo_factory import create_vector_2d


class AngleUnit(Enum):
    DEGREE = 360.0
    RADIAN = 2 * math.pi

    def __init__(self, cyclic_value: float):
        self._cyclic_value = cyclic_value

    @property
    def cyclic_value(self) -> float:
        return self._cyclic_value


class Angle:
    def __init__(self, value: float, unit: AngleUnit):
        self.__value = _calc_cyclic_value(value, unit.cyclic_value)
        self.__unit = unit

    def __eq__(self, other: Angle):
        return _calc_first_cycle_equivalent(self).in_degrees() == \
               _calc_first_cycle_equivalent(other).in_degrees()

    def in_degrees(self) -> float:
        return self.__value if self.__unit is AngleUnit.DEGREE else math.degrees(self.__value)

    def in_radians(self) -> float:
        return self.__value if self.__unit is AngleUnit.RADIAN else math.radians(self.__value)

    def to_direction(self) -> Vector2D:
        return create_vector_2d(math.cos(self.in_radians()), math.sin(self.in_radians()))

    def calc_reverse(self) -> Angle:
        return Angle(self.in_degrees() + AngleUnit.DEGREE.cyclic_value / 2, AngleUnit.DEGREE)

    def calc_abs_difference(self, other: Angle) -> Angle:
        if self.__unit is not other.__unit:
            raise ValueError("error, angle units are not equal")
        angle_1 = _calc_first_cycle_equivalent(self)
        angle_2 = _calc_first_cycle_equivalent(other)
        return Angle(abs(angle_1.in_degrees() - angle_2.in_degrees()), AngleUnit.DEGREE)

    def __str__(self):
        return "Angle ({0}, {1})".format(self.__value, self.__unit)


def _calc_first_cycle_equivalent(angle: Angle):
    # convert the angle to be between 0 [deg] and 360 [deg]
    cyclic_value_deg = AngleUnit.DEGREE.cyclic_value
    return Angle(_calc_cyclic_value(angle.in_degrees(), cyclic_value_deg), AngleUnit.DEGREE)


def _calc_cyclic_value(value: float, cyclic_value: float) -> float:
    return ((value % cyclic_value) + cyclic_value) % cyclic_value


class AngleUniformDistribution(UniformDistribution):

    def __init__(self, start_angle: Angle, end_angle: Angle):
        super().__init__(Range(start_angle.in_degrees(), end_angle.in_degrees()))

    def choose_rand(self, random: Random) -> Angle:
        return Angle(super(AngleUniformDistribution, self).choose_rand(random), AngleUnit.DEGREE)
