from __future__ import annotations

from abc import ABC
from typing import Union, List


class Geometry2D(ABC):

    @property
    def type(self) -> str:
        raise NotImplementedError()


class Vector2D(Geometry2D):

    @property
    def type(self) -> str:
        raise NotImplementedError()

    @property
    def x(self) -> float:
        raise NotImplementedError()

    @property
    def y(self) -> float:
        raise NotImplementedError()

    def add(self, other_vector: Vector2D) -> Vector2D:
        raise NotImplementedError()

    def subtract(self, other_vector: Vector2D) -> Vector2D:
        raise NotImplementedError

    def reverse(self) -> Vector2D:
        raise NotImplementedError()

    def to_point(self) -> Point2D:
        raise NotImplementedError()

    def dot(self, other_vector: Vector2D) -> float:
        raise NotImplementedError()

    def __add__(self, other: Vector2D) -> Vector2D:
        raise NotImplementedError()

    def __sub__(self, other: Vector2D) -> Vector2D:
        raise NotImplementedError()

    def __mul__(self, other: float) -> Vector2D:
        raise NotImplementedError()

    def __eq__(self, other) -> bool:
        raise NotImplementedError()


class Point2D(Geometry2D):

    @property
    def type(self) -> str:
        raise NotImplementedError()

    @property
    def x(self) -> float:
        raise NotImplementedError()

    @property
    def y(self) -> float:
        raise NotImplementedError()

    def subtract(self, other_point: Point2D) -> Vector2D:
        raise NotImplementedError()

    def add_vector(self, vector: Vector2D) -> Point2D:
        raise NotImplementedError()

    def to_vector(self) -> Vector2D:
        raise NotImplementedError()

    def calc_distance_to_point(self, other_point: Point2D) -> float:
        raise NotImplementedError()

    def __eq__(self, other) -> bool:
        raise NotImplementedError()


class Curve2D(Geometry2D):

    @property
    def type(self) -> str:
        raise NotImplementedError()

    @property
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    def calc_length(self):
        raise NotImplementedError()


class LineString2D(Curve2D):

    @property
    def type(self) -> str:
        raise NotImplementedError()

    @property
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    def calc_length(self):
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()


class LinearRing2D(LineString2D):
    # The Linear Ring is a 2d line string in which the first point is also the last point, forming a closed loop.

    @property
    def type(self) -> str:
        raise NotImplementedError()

    @property
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    def calc_length(self):
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()


class Polygon2D(Geometry2D):

    @property
    def type(self) -> str:
        raise NotImplementedError()

    @property
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    @property
    def boundary(self) -> LinearRing2D:
        raise NotImplementedError()

    def calc_area(self) -> float:
        raise NotImplementedError()

    def calc_intersection(self, other_polygon: Polygon2D) -> Union[Polygon2D, MultiPolygon2D]:
        raise NotImplementedError()


class MultiPolygon2D(Geometry2D):

    @property
    def type(self) -> str:
        raise NotImplementedError()

    def calc_area(self) -> float:
        raise NotImplementedError()
