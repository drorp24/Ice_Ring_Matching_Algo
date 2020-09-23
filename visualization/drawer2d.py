from __future__ import annotations

from abc import ABC, abstractmethod

from geometry.geo2d import Point2D, Vector2D, Polygon2D, LineString2D, LinearRing2D


class Drawer2d(ABC):
    @abstractmethod
    def add_point2d(self, point2d: Point2D):
        pass

    @abstractmethod
    def add_vector2d(self, vector2d: Vector2D):
        pass

    @abstractmethod
    def add_line_string2d(self, line_string2d: LineString2D):
        pass

    @abstractmethod
    def add_linear_ring2d(self, linear_ring2d: LinearRing2D):
        pass

    @abstractmethod
    def add_polygon2d(self, polygon2d: Polygon2D):
        pass

    @abstractmethod
    def draw(self):
        pass

#from geometry.geo_factory import Geo2D


# p1 = Geo2D.create_point_2d(10, 200)
# p2 = Geo2D.create_point_2d(100, 200)
#
# print(p1.subtract_point(p2))
#
# print(p1.add_vector(Geo2D.convert_to_vector(p2)))
#
# print(p1.calc_distance_to_point(p2))

