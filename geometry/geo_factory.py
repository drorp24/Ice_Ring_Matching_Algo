from __future__ import annotations

from typing import List

from geometry.geo2d import Point2D, Vector2D, Polygon2D, LineString2D, LinearRing2D
from geometry.math_wrapper import MathVector2D
from geometry.shapely_wrapper import ShapelyPoint2D, ShapelyPolygon2D, ShapelyLineString2D, ShapelyLinearRing2D


def create_point_2d(x: float, y: float) -> Point2D:
    return ShapelyPoint2D(x, y)


def convert_to_point(vector: Vector2D) -> Point2D:
    return create_point_2d(vector.x, vector.y)


def create_vector_2d(x: float, y: float) -> Vector2D:
    return MathVector2D(x, y)


def convert_to_vector(point: Point2D) -> Vector2D:
    return create_vector_2d(point.x, point.y)


def create_polygon_2d(points: List[Point2D]) -> Polygon2D:
    return ShapelyPolygon2D(create_linear_ring_2d(points))


def create_linestring_2d(points: List[Point2D]) -> LineString2D:
    return ShapelyLineString2D(points)


def create_linear_ring_2d(points: List[Point2D]) -> LinearRing2D:
    return ShapelyLinearRing2D(points)
