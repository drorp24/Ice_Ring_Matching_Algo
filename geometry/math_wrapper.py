from __future__ import annotations

from math import sqrt
from typing import Union

from geometry.geo2d import Vector2D


class MathVector2D(Vector2D):

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
        self._type = 'Vector'

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def type(self) -> str:
        return self._type

    def dot_product(self, other: Vector2D) -> float:
        return self.x * other.x + self.y * other.y

    def add_vector(self, other_vector: Vector2D) -> Vector2D:
        return self + other_vector

    def subtract_vector(self, other_vector: Vector2D) -> Vector2D:
        return self - other_vector

    def reverse_vector(self) -> Vector2D:
        return self * -1

    def to_point(self):
        from geometry.geo_factory import convert_to_point
        return convert_to_point(self)

    def __add__(self, other: Vector2D) -> Vector2D:
        return MathVector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return MathVector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Union[float, Vector2D]) -> Vector2D:
        """scalar vector multiplication"""
        if isinstance(other, (float, int)):
            return MathVector2D(self.x * other, self.y * other)
        """point-wise multiplication"""
        return MathVector2D(self.x * other.x, self.y * other.y)

    def __abs__(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def __str__(self) -> str:
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)


