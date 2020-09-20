from __future__ import annotations

from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry

from geometry.geo2d import Point2D, Vector2D


class ShapelyGeometry(object):

    def __init__(self, _shapely_obj: BaseGeometry):
        self._shapely_obj = _shapely_obj

    @property
    def shapely_obj(self):
        return self._shapely_obj

    @property
    def type(self) -> str:
        return self._shapely_obj.type


class ShapelyPoint2D(ShapelyGeometry, Point2D):

    def __init__(self, x: float, y: float):
        super().__init__(Point(x, y))

    @property
    def x(self) -> float:
        return self._shapely_obj.x

    @property
    def y(self) -> float:
        return self._shapely_obj.y

    def shapely_obj(self):
        return self._shapely_obj

    def subtract_point(self, other_point: Point2D) -> Vector2D:
        return self.to_vector() - other_point.to_vector()

    def add_vector(self, vector: Vector2D) -> Point2D:
        return ShapelyPoint2D(self.x + vector.x, self.y + vector.y)

    def calc_distance_to_point(self, other_point: ShapelyPoint2D) -> float:
        return self.shapely_obj().distance(other_point.shapely_obj())

    def to_vector(self):
        from geometry.geo_factory import Geo2D
        return Geo2D.convert_to_vector(self)

    def __str__(self) -> str:
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)
