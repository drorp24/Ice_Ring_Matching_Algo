from __future__ import annotations

from abc import ABC, abstractmethod

from geometry.geo2d import Point2D, Vector2D, Polygon2D, LineString2D, LinearRing2D


class Drawer2D(ABC):
    @abstractmethod
    def add_point2d(self, point2d: Point2D, edgecolor='black', facecolor='black', linewidth=2):
        pass

    @abstractmethod
    def add_vector2d(self, vector2d: Vector2D, edgecolor='black', facecolor='black', linewidth=2):
        pass

    @abstractmethod
    def add_line_string2d(self, line_string2d: LineString2D, edgecolor='black', facecolor='black', linewidth=2):
        pass

    @abstractmethod
    def add_linear_ring2d(self, linear_ring2d: LinearRing2D, edgecolor='black', facecolor='black', linewidth=2):
        pass

    @abstractmethod
    def add_polygon2d(self, polygon2d: Polygon2D, edgecolor='black', facecolor='black', linewidth=2):
        pass

    @abstractmethod
    def add_arrow2d(self, tail: Point2D, head: Point2D, edgecolor='black', facecolor='black', linewidth=2):
        pass

    @abstractmethod
    def draw(self, block=True):
        """
        Parameters
        ----------
        block : bool, optional

            If `True` block and run the GUI main loop until all windows
            are closed.

            If `False` ensure that all windows are displayed and return
            immediately.  In this case, you are responsible for ensuring
            that the event loop is running to have responsive figures.

            * Useful to draw multiple figures: all the drawers should not block except the last one.
        """

        pass

