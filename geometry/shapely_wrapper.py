from __future__ import annotations

from typing import List, Tuple, Iterator

from shapely.geometry import Point, Polygon, LineString, LinearRing
from shapely.geometry.base import BaseGeometry

from geometry.geo2d import Point2D, Vector2D, Polygon2D, MultiPolygon2D, LineString2D, LinearRing2D


class ShapelyGeometry(object):

    def __init__(self, _shapely_obj: BaseGeometry):
        self._shapely_obj = _shapely_obj

    @property
    def __shapely_obj(self) -> BaseGeometry:
        return self._shapely_obj

    @staticmethod
    def create_from_shapely(geo: BaseGeometry):
        raise NotImplementedError

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

    @staticmethod
    def create_from_shapely(point: Point):
        return ShapelyPoint2D(point.x, point.y)

    @property
    def __shapely_obj(self) -> Point:
        return Point(self._shapely_obj)

    def subtract_point(self, other_point: Point2D) -> Vector2D:
        return self.to_vector() - other_point.to_vector()

    def add_vector(self, vector: Vector2D) -> Point2D:
        return ShapelyPoint2D(self.x + vector.x, self.y + vector.y)

    def calc_distance_to_point(self, other_point: ShapelyPoint2D) -> float:
        return self.__shapely_obj.distance(other_point.__shapely_obj)

    def to_vector(self):
        from geometry.geo_factory import convert_to_vector
        return convert_to_vector(self)

    def to_tuple(self) -> Tuple:
        return self.x, self.y

    def __str__(self) -> str:
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, other: Point2D):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash(self.to_tuple())


class ShapelyLineString2D(ShapelyGeometry, LineString2D):

    def __init__(self, points: List[Point2D]):
        super().__init__(LineString(ShapelyUtils.convert_points_list_to_xy_array(points)))

    @staticmethod
    def create_from_shapely(line_string: LineString):
        return ShapelyLinearRing2D(ShapelyUtils.convert_xy_array_to_points_list(line_string.xy))

    @classmethod
    def create_from_xy_array(cls, xy_array: List[Tuple[float, float]]) -> LineString2D:
        return ShapelyLineString2D(ShapelyUtils.convert_xy_array_to_points_list(xy_array))

    @property
    def __shapely_obj(self) -> LineString:
        return LineString(self._shapely_obj)

    @property
    def points(self) -> List[Point2D]:
        return ShapelyUtils.convert_xy_separate_arrays_to_points_list(self.__shapely_obj.xy)

    def calc_length(self) -> float:
        return self.__shapely_obj.length

    def __eq__(self, other: LineString2D):
        return self.points == other.points


class ShapelyLinearRing2D(ShapelyGeometry, LinearRing2D):

    def __init__(self, points: List[Point2D]):
        super().__init__(LinearRing(ShapelyUtils.convert_points_list_to_xy_array(points)))

    @staticmethod
    def create_from_shapely(linear_ring: LinearRing):
        return ShapelyLinearRing2D(ShapelyUtils.convert_xy_array_to_points_list(linear_ring.xy))

    @property
    def __shapely_obj(self) -> LineString:
        return LinearRing(self._shapely_obj)

    @property
    def points(self) -> List[Point2D]:
        x, y = self.__shapely_obj.xy
        return ShapelyUtils.convert_xy_separate_arrays_to_points_list(x.tolist(), y.tolist())

    def calc_length(self) -> float:
        return self.__shapely_obj.length

    def __len__(self) -> float:
        return self.calc_length()

    def __eq__(self, other):
        pass


class ShapelyPolygon2D(ShapelyGeometry, Polygon2D):

    def __init__(self, boundary: LinearRing2D):
        super().__init__(Polygon(ShapelyUtils.convert_points_list_to_xy_array(boundary.points)))

    @staticmethod
    def create_from_shapely(polygon: Polygon):
        x_array, y_array = polygon.exterior.xy
        points_list_shapely = ShapelyUtils.convert_xy_separate_arrays_to_points_list(x_array, y_array)
        return ShapelyPolygon2D(ShapelyLinearRing2D(points_list_shapely))

    @property
    def __shapely_obj(self) -> Polygon:
        return Polygon(self._shapely_obj)

    @property
    def boundary(self) -> LineString2D:
        return ShapelyLineString2D(self.points)

    @property
    def points(self) -> List[Point2D]:
        x_array, y_array = self.__shapely_obj.exterior.xy
        return ShapelyUtils.convert_xy_separate_arrays_to_points_list(x_array[:-1], y_array[:-1])

    def calc_area(self) -> float:
        return self.__shapely_obj.area

    def calc_intersection(self, other_polygon: Polygon2D) -> [Polygon2D, MultiPolygon2D]:
        try:
            other_polygon_shapely = other_polygon.__shapely_obj
        except NonShapelyNativeGeometry:
            other_polygon_shapely = ShapelyUtils.convert_polygon2d_to_shapely(other_polygon)
        return ShapelyPolygon2D.create_from_shapely(self.__shapely_obj.intersection(other_polygon_shapely))


class ShapelyUtils:

    @staticmethod
    def convert_xy_array_to_points_list(xy_array: Iterator[Tuple[float, float]]) -> List[Point2D]:
        return [ShapelyPoint2D(xy[0], xy[1]) for xy in xy_array]

    @staticmethod
    def convert_xy_separate_arrays_to_points_list(x_array: List[float], y_array: List[float]) -> List[Point2D]:
        return ShapelyUtils.convert_xy_array_to_points_list(zip(x_array, y_array))

    @staticmethod
    def convert_points_list_to_xy_array(points: List[Point2D]) -> List[Tuple[float, float]]:
        return [(p.x, p.y) for p in points]

    @staticmethod
    def convert_polygon2d_to_shapely(polygon: Polygon2D) -> Polygon:
        return Polygon(ShapelyUtils.convert_points_list_to_xy_array(polygon.points))

    @staticmethod
    def convert_linear_ring2d_to_shapely(linear_ring: LinearRing2D) -> LinearRing:
        return LinearRing(ShapelyUtils.convert_points_list_to_xy_array(linear_ring.points))


    @staticmethod
    def convert_line_string2d_to_shapely(line_string: LineString2D) -> LineString:
        return LineString(ShapelyUtils.convert_points_list_to_xy_array(line_string.points))

    @staticmethod
    def convert_point2d_to_shapely(point: Point2D) -> Point:
        return Point(point.x, point.y)


class NonShapelyNativeGeometry(Exception):
    """
    Given operations requiring Shapely Geometry, an exception defining a non-shapely geometry will be used to validate.
    """
    pass
