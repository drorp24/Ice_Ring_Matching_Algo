from __future__ import annotations

import math
from abc import ABC, abstractmethod
from enum import Enum

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


class BaseAngle(ABC):

    @abstractmethod
    def in_degrees(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def in_radians(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def to_direction(self) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def calc_reverse(self) -> BaseAngle:
        raise NotImplementedError()

    @abstractmethod
    def calc_abs_difference(self, other: Angle) -> BaseAngle:
        raise NotImplementedError()


class Angle(BaseAngle):
    def __init__(self, value: float, unit: AngleUnit):
        super().__init__()

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

    def calc_reverse(self) -> BaseAngle:
        return Angle(self.in_degrees() + AngleUnit.DEGREE.cyclic_value / 2, AngleUnit.DEGREE)

    def calc_abs_difference(self, other: Angle) -> BaseAngle:
        if self.__unit is not other.__unit:
            raise ValueError("error, angle units are not equal")
        angle_1 = _calc_first_cycle_equivalent(self)
        angle_2 = _calc_first_cycle_equivalent(other)
        return Angle(abs(angle_1.in_degrees() - angle_2.in_degrees()), AngleUnit.DEGREE)

    def __str__(self):
        return "Angle ({0}, {1})".format(self.__value, self.__unit)


class NoneAngle(BaseAngle):
    def in_degrees(self) -> float:
        raise NotImplementedError()

    def in_radians(self) -> float:
        raise NotImplementedError()

    def to_direction(self) -> Vector2D:
        raise NotImplementedError()

    def calc_reverse(self) -> BaseAngle:
        raise NotImplementedError()

    def calc_abs_difference(self, other: Angle) -> BaseAngle:
        raise NotImplementedError()

    def __init__(self):
        super().__init__()


def _calc_first_cycle_equivalent(angle: Angle):
    # convert the angle to be between 0 [deg] and 360 [deg]
    cyclic_value_deg = AngleUnit.DEGREE.cyclic_value
    return Angle(_calc_cyclic_value(angle.in_degrees(), cyclic_value_deg), AngleUnit.DEGREE)


def _calc_cyclic_value(value: float, cyclic_value: float) -> float:
    return ((value % cyclic_value) + cyclic_value) % cyclic_value
