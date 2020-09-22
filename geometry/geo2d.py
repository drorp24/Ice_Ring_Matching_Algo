from __future__ import annotations

from abc import ABC


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

