from __future__ import annotations

from abc import ABC, abstractmethod

from geometry.geo2d import Point2D, Polygon2D, LineString2D, LinearRing2D


class Drawer2D(ABC):
    @abstractmethod
    def add_point2d(self, point2d: Point2D):
        raise NotImplementedError

    @abstractmethod
    def add_line_string2d(self, line_string2d: LineString2D):
        raise NotImplementedError

    @abstractmethod
    def add_linear_ring2d(self, linear_ring2d: LinearRing2D):
        raise NotImplementedError

    @abstractmethod
    def add_polygon2d(self, polygon2d: Polygon2D):
        raise NotImplementedError

    @abstractmethod
    def draw(self):
        raise NotImplementedError
