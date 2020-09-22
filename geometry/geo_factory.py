from __future__ import annotations

from geometry.geo2d import Point2D, Vector2D
from geometry.math_wrapper import _MathVector2D
from geometry.shapely_wrapper import _ShapelyPoint2D


def create_point_2d(x: float, y: float) -> Point2D:
    return _ShapelyPoint2D(x, y)


def convert_to_point(vector: Vector2D) -> Point2D:
    return create_point_2d(vector.x, vector.y)


def create_vector_2d(x: float, y: float) -> Vector2D:
    return _MathVector2D(x, y)


def convert_to_vector(point: Point2D) -> Vector2D:
    return create_vector_2d(point.x, point.y)
