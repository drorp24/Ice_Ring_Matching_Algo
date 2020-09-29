from __future__ import annotations

from typing import List

from geometry.geo2d import Point2D, Vector2D
from geometry.geo2d import Polygon2D, LineString2D, LinearRing2D
from geometry.math_wrapper import _MathVector2D
from geometry.shapely_wrapper import _ShapelyPoint2D, _ShapelyUtils
from geometry.shapely_wrapper import _ShapelyPolygon2D, _ShapelyLineString2D, _ShapelyLinearRing2D
from matplotlib.patches import Ellipse


def create_point_2d(x: float, y: float) -> Point2D:
    return _ShapelyPoint2D(x, y)


def convert_to_point(vector: Vector2D) -> Point2D:
    return create_point_2d(vector.x, vector.y)


def create_vector_2d(x: float, y: float) -> Vector2D:
    return _MathVector2D(x, y)


def convert_to_vector(point: Point2D) -> Vector2D:
    return create_vector_2d(point.x, point.y)


def create_polygon_2d(points: List[Point2D]) -> Polygon2D:
    return _ShapelyPolygon2D(create_linear_ring_2d(points))


def create_polygon_2d_from_ellipsis(center_xy, width, height, rotation) -> Polygon2D:
    plt_ellipsis = Ellipse(center_xy, width, height, rotation)
    vertices = plt_ellipsis.get_verts()
    return create_polygon_2d(_ShapelyUtils.convert_xy_array_to_points_list(vertices))


def create_line_string_2d(points: List[Point2D]) -> LineString2D:
    return _ShapelyLineString2D(points)


def create_linear_ring_2d(points: List[Point2D]) -> LinearRing2D:
    return _ShapelyLinearRing2D(points)
