from __future__ import annotations

from functools import reduce
from typing import List, Union

from matplotlib.patches import Ellipse

from geometry.geo2d import Point2D, Vector2D, MultiPolygon2D, EmptyGeometry2D, Bbox2D
from geometry.geo2d import Polygon2D, LineString2D, LinearRing2D
from geometry.math_wrapper import _MathVector2D
from geometry.shapely_wrapper import _ShapelyMultiPolygon2D, _ShapelyEmptyGeometry, _ShapelyBbox2D
from geometry.shapely_wrapper import _ShapelyPoint2D
from geometry.shapely_wrapper import _ShapelyPolygon2D, _ShapelyLineString2D, _ShapelyLinearRing2D
from geometry.utils import GeometryUtils


def create_empty_geometry_2d() -> EmptyGeometry2D:
    return _ShapelyEmptyGeometry()


def create_point_2d(x: float, y: float) -> Point2D:
    return _ShapelyPoint2D(x, y)


def convert_dict_to_point_2d(input_dict: dict):
    return _ShapelyPoint2D.dict_to_obj(dict_input=input_dict)


def convert_to_point(vector: Vector2D) -> Point2D:
    return create_point_2d(vector.x, vector.y)


def create_vector_2d(x: float, y: float) -> Vector2D:
    return _MathVector2D(x, y)


def convert_to_vector(point: Point2D) -> Vector2D:
    return create_vector_2d(point.x, point.y)


def create_polygon_2d(points: List[Point2D]) -> Polygon2D:
    assert set(points).__len__() >= 3
    return _ShapelyPolygon2D(points)


def create_multipolygon_2d(polygons: List[Polygon2D]) -> MultiPolygon2D:
    return _ShapelyMultiPolygon2D(polygons)


def create_bbox(min_x: float, min_y: float, max_x: float, max_y: float) -> Bbox2D:
    min_point = create_point_2d(min_x, min_y)
    max_point = create_point_2d(max_x, max_y)
    return _ShapelyBbox2D(min_point, max_point)


def create_polygon_2d_from_ellipse(ellipse_center: Point2D, ellipse_width: float, ellipse_height: float,
                                   ellipse_rotation_deg: float,
                                   epsilon_dist=0.0001) -> Union[Polygon2D, EmptyGeometry2D]:
    plt_ellipse = Ellipse(ellipse_center.xy(), ellipse_width, ellipse_height, ellipse_rotation_deg)
    vertices = plt_ellipse.get_verts()
    if ellipse_width < epsilon_dist or ellipse_height < epsilon_dist:
        return _ShapelyEmptyGeometry()
    return create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(vertices))


def create_line_string_2d(points: List[Point2D]) -> LineString2D:
    return _ShapelyLineString2D(points)


def create_linear_ring_2d(points: List[Point2D]) -> LinearRing2D:
    return _ShapelyLinearRing2D(points)


def calc_centroid(points: [Point2D]) -> Point2D:
    return (reduce(lambda p, j: p + j, points).to_vector() * (1.0 / points.__len__())).to_point()
