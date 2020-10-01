from __future__ import annotations

from typing import List

from geometry.geo2d import Point2D, Vector2D, MultiPolygon2D, EmptyGeometry2D
from geometry.geo2d import Polygon2D, LineString2D, LinearRing2D
from geometry.math_wrapper import _MathVector2D
from geometry.shapely_wrapper import _ShapelyPoint2D, _ShapelyMultiPolygon2D, _ShapelyEmptyGeometry
from geometry.shapely_wrapper import _ShapelyPolygon2D, _ShapelyLineString2D, _ShapelyLinearRing2D


def create_empty_geometry_2d() -> EmptyGeometry2D:
    return _ShapelyEmptyGeometry()


def create_point_2d(x: float, y: float) -> Point2D:
    return _ShapelyPoint2D(x, y)


def convert_to_point(vector: Vector2D) -> Point2D:
    return create_point_2d(vector.x, vector.y)


def create_vector_2d(x: float, y: float) -> Vector2D:
    return _MathVector2D(x, y)


def convert_to_vector(point: Point2D) -> Vector2D:
    return create_vector_2d(point.x, point.y)


def create_polygon_2d(points: List[Point2D]) -> Polygon2D:
    return _ShapelyPolygon2D(points)


def create_multipolygon_2d(polygons: List[Polygon2D]) -> MultiPolygon2D:
    return _ShapelyMultiPolygon2D(polygons)


def create_line_string_2d(points: List[Point2D]) -> LineString2D:
    return _ShapelyLineString2D(points)


def create_linear_ring_2d(points: List[Point2D]) -> LinearRing2D:
    return _ShapelyLinearRing2D(points)
