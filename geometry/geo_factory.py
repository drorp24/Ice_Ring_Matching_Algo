from __future__ import annotations

from geometry.geo2d import Point2D, Vector2D
from geometry.math_wrapper import MathVector2D
from geometry.shapely_wrapper import ShapelyPoint2D


class Geo2D:

    @staticmethod
    def create_point_2d(x: float, y: float) -> Point2D:
        return ShapelyPoint2D(x, y)

    @staticmethod
    def convert_to_point(vector: Vector2D) -> Point2D:
        return Geo2D.create_point_2d(vector.x, vector.y)

    @staticmethod
    def create_vector_2d(x: float, y: float) -> Vector2D:
        return MathVector2D(x, y)

    @staticmethod
    def convert_to_vector(point: Point2D) -> Vector2D:
        return Geo2D.create_vector_2d(point.x, point.y)
