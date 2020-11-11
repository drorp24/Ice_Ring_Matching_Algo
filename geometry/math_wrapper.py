from __future__ import annotations

from math import sqrt

from geometry.geo2d import Vector2D, Point2D


class _MathVector2D(Vector2D):

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
        self._type = 'Vector'

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def _geo_type(self) -> str:
        return self._type

    @property
    def norm(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def dot(self, other: Vector2D) -> float:
        return self.x * other.x + self.y * other.y

    def add(self, other_vector: Vector2D) -> Vector2D:
        return self + other_vector

    def subtract(self, other_vector: Vector2D) -> Vector2D:
        return self - other_vector

    def multiply(self, scale: float) -> Vector2D:
        return self * scale

    def reverse(self) -> Vector2D:
        return self * -1

    def to_point(self) -> Point2D:
        from geometry.geo_factory import convert_to_point
        return convert_to_point(self)

    def __add__(self, other: Vector2D) -> Vector2D:
        return _MathVector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return _MathVector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scale: (float, int)) -> Vector2D:
        """scalar vector multiplication"""
        return _MathVector2D(self.x * scale, self.y * scale)

    def __abs__(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def __str__(self) -> str:
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, other) -> bool:
        return (self.x, self.y) == (other.x, other.y)
