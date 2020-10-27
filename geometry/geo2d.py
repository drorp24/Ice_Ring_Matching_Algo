from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union, List


class Geometry2D(ABC):

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()


class EmptyGeometry2D(Geometry2D):
    """
    Geometry is empty if it has no points and it does not contain geometric information.
    Empty geometries can be introduced when editing or creating geometries.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def calc_area(self) -> float:
        raise NotImplementedError()


class Vector2D(Geometry2D):

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def x(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def y(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def add(self, other_vector: Vector2D) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def subtract(self, other_vector: Vector2D) -> Vector2D:
        raise NotImplementedError

    @abstractmethod
    def reverse(self) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def to_point(self) -> Point2D:
        raise NotImplementedError()

    @abstractmethod
    def dot(self, other_vector: Vector2D) -> float:
        raise NotImplementedError()

    @abstractmethod
    def __add__(self, other: Vector2D) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def __sub__(self, other: Vector2D) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def __mul__(self, other: float) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError()


class Point2D(Geometry2D):

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def x(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def y(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def xy(self) -> (float, float):
        raise NotImplementedError()

    @abstractmethod
    def subtract(self, other_point: Point2D) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def add_vector(self, vector: Vector2D) -> Point2D:
        raise NotImplementedError()

    @abstractmethod
    def to_vector(self) -> Vector2D:
        raise NotImplementedError()

    @abstractmethod
    def calc_distance_to_point(self, other_point: Point2D) -> float:
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError()


class Curve2D(Geometry2D):

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    @abstractmethod
    def calc_length(self):
        raise NotImplementedError()


class LineString2D(Curve2D):

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    @abstractmethod
    def calc_length(self):
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError()


class LinearRing2D(LineString2D):
    """
        The Linear Ring is a 2d line string in which the first point is also the last point, forming a closed loop.
        The is NO need to initialize with duplicate points in start and end.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    @abstractmethod
    def calc_length(self):
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError()


class Surface2D(ABC):
    """
        Surface represents any 2D object with positive area.
    """

    @abstractmethod
    def calc_area(self) -> float:
        raise NotImplementedError()


class Polygon2D(Geometry2D, Surface2D):
    """
        Polygon acts as a standard 2d polygon.
        * Closed 2D Shape, without overlapping, potentially with holes.
        * The convention for initialization is  we utilize is NOT to duplicate the end points,
        the implementation will "close" the polygon loop.
    """
    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def points(self) -> List[Point2D]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def holes(self) -> List[LinearRing2D]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def boundary(self) -> LinearRing2D:
        raise NotImplementedError()

    @property
    def bbox(self) -> Bbox2D:
        raise NotImplementedError()

    @abstractmethod
    def calc_area(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def calc_intersection(self, other_polygon: Polygon2D) -> Union[Polygon2D, MultiPolygon2D, EmptyGeometry2D]:
        raise NotImplementedError()

    @abstractmethod
    def calc_difference(self, other_polygon: Polygon2D) -> Union[Polygon2D, MultiPolygon2D, EmptyGeometry2D]:
        raise NotImplementedError()

    @abstractmethod
    def calc_union(self, other_polygon: Polygon2D) -> Union[Polygon2D, MultiPolygon2D]:
        raise NotImplementedError()


class MultiPolygon2D(Geometry2D, Surface2D):

    """
        Multi-polygon represents a set of polygons.
        * The polygons can NOT overlap.
        * Other geometries will not be included within MultiPolygon.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def calc_area(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def to_polygons(self) -> List[Polygon2D]:
        raise NotImplementedError()


class Bbox2D(Polygon2D):

    """
        Bbox2D represents a (minx, miny, maxx, maxy) tuple (float values)
        that bounds an object.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def min_x(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def min_y(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def max_x(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def max_y(self) -> float:
        raise NotImplementedError()
