from __future__ import annotations

from typing import List, Tuple, Union
from shapely.geometry import Point, Polygon, LineString, LinearRing, MultiPolygon
from shapely.geometry.base import BaseGeometry, EmptyGeometry

from geometry.geo2d import Point2D, Vector2D, Polygon2D, MultiPolygon2D, LineString2D, LinearRing2D, EmptyGeometry2D
from geometry.utils import GeometryUtils

EPSILON_FOR_EQUAL_AREA: float = 0.00001


class _ShapelyGeometry(object):

    def __init__(self, shapely_obj: BaseGeometry):
        self.__shapely_obj = shapely_obj

    @property
    def _shapely_obj(self) -> BaseGeometry:
        return self.__shapely_obj

    @property
    def type(self) -> str:
        return self._shapely_obj.type

    def is_empty(self) -> bool:
        return self.__shapely_obj.is_empty or isinstance(self, _ShapelyEmptyGeometry)


class _ShapelyEmptyGeometry(_ShapelyGeometry, EmptyGeometry2D):

    def __init__(self):
        super().__init__(EmptyGeometry())

    @property
    def _shapely_obj(self) -> EmptyGeometry:
        return self._shapely_obj

    def calc_area(self) -> float:
        return 0

    def __eq__(self, other):
        return isinstance(other, EmptyGeometry2D)


class _ShapelyPoint2D(_ShapelyGeometry, Point2D):

    def __init__(self, x: float, y: float):
        super().__init__(Point(x, y))

    @property
    def x(self) -> float:
        return self._shapely_obj.x

    @property
    def y(self) -> float:
        return self._shapely_obj.y

    def xy(self) -> (float, float):
        return self.x, self.y

    @property
    def _shapely_obj(self) -> Point:
        return super()._shapely_obj

    def subtract(self, other_point: Point2D) -> Vector2D:
        return self.to_vector() - other_point.to_vector()

    def add_vector(self, vector: Vector2D) -> Point2D:
        return _ShapelyPoint2D(self.x + vector.x, self.y + vector.y)

    def calc_distance_to_point(self, other_point: Point2D) -> float:
        if isinstance(other_point, _ShapelyPoint2D):
            return self._shapely_obj.distance(other_point._shapely_obj)
        return self._shapely_obj.distance(_ShapelyUtils.convert_point2d_to_shapely(other_point))

    def to_vector(self) -> Vector2D:
        from geometry.geo_factory import convert_to_vector
        return convert_to_vector(self)

    def to_tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    def __str__(self) -> str:
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, other) -> bool:
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash(self.to_tuple())

    def __dict__(self):
        return {'x': self.x, 'y': self.y}

    def __repr__(self):
        return str(self.__dict__())


class _ShapelyLineString2D(_ShapelyGeometry, LineString2D):

    def __init__(self, points: List[Point2D]):
        super().__init__(LineString(GeometryUtils.convert_points_list_to_xy_array(points)))

    @staticmethod
    def _create_from_shapely(line_string: LineString) -> LineString2D:
        return _ShapelyLinearRing2D(GeometryUtils.convert_xy_array_to_points_list(line_string.xy))

    @classmethod
    def create_from_xy_array(cls, xy_array: List[Tuple[float, float]]) -> LineString2D:
        return _ShapelyLineString2D(GeometryUtils.convert_xy_array_to_points_list(xy_array))

    @property
    def _shapely_obj(self) -> LineString:
        return super()._shapely_obj

    @property
    def points(self) -> List[Point2D]:
        x_array, y_array = self._shapely_obj.xy
        return GeometryUtils.convert_xy_separate_arrays_to_points_list(x_array, y_array)

    def calc_length(self) -> float:
        return self._shapely_obj.length

    def __eq__(self, other: LineString2D):
        return self.points == other.points


class _ShapelyLinearRing2D(_ShapelyGeometry, LinearRing2D):

    def __init__(self, points: List[Point2D]):
        super().__init__(LinearRing(GeometryUtils.convert_points_list_to_xy_array(points)))

    @staticmethod
    def _create_from_shapely(linear_ring: LinearRing):
        return

    @property
    def _shapely_obj(self) -> LinearRing:
        return super()._shapely_obj

    @property
    def points(self) -> List[Point2D]:
        x_array, y_array = self._shapely_obj.xy
        return GeometryUtils.convert_xy_separate_arrays_to_points_list(x_array.tolist(), y_array.tolist())

    def calc_length(self) -> float:
        return self._shapely_obj.length

    def __len__(self) -> float:
        return self.calc_length()

    def __eq__(self, other):
        return self.points == other.points


class _ShapelyPolygon2D(_ShapelyGeometry, Polygon2D):

    def __init__(self, boundary_points: List[Point2D]):
        super().__init__(Polygon(GeometryUtils.convert_points_list_to_xy_array(boundary_points)))

    @classmethod
    def create_from_linear_ring(cls, boundary: LinearRing2D) -> Polygon2D:
        return _ShapelyPolygon2D(boundary.points)

    @property
    def _shapely_obj(self) -> Polygon:
        return super()._shapely_obj

    @property
    def holes(self) -> List[LinearRing2D]:
        raise NotImplementedError

    @property
    def boundary(self) -> LinearRing2D:
        return _ShapelyLinearRing2D(self.points)

    @property
    def points(self) -> List[Point2D]:
        if self._shapely_obj.is_empty:
            return []
        x_array, y_array = self._shapely_obj.exterior.xy
        return GeometryUtils.convert_xy_separate_arrays_to_points_list(x_array[:-1], y_array[:-1])

    def calc_area(self) -> float:
        return self._shapely_obj.area

    def calc_intersection(self, other_polygon: Polygon2D) -> Union[EmptyGeometry2D, Polygon2D, MultiPolygon2D]:
        other_polygon_shapely = _ShapelyUtils.convert_polygon2d_to_shapely(other_polygon)
        if not other_polygon_shapely.is_valid or not self._shapely_obj.is_valid:
            raise InvalidGeometryException("Problem with internal geometry, not able to apply intersection")
        internal_geometry = self._shapely_obj.intersection(other_polygon_shapely)
        return _ShapelyUtils.convert_shapely_to_surface_2d(internal_geometry)

    def calc_difference(self, other_polygon: Polygon2D) -> Union[EmptyGeometry2D, Polygon2D, MultiPolygon2D]:
        other_polygon_shapely = _ShapelyUtils.convert_polygon2d_to_shapely(other_polygon)
        if not other_polygon_shapely.is_valid or not self._shapely_obj.is_valid:
            raise InvalidGeometryException("Problem with internal geometry, not able to apply difference")
        internal_geometry = self._shapely_obj.difference(other_polygon_shapely)
        return _ShapelyUtils.convert_shapely_to_surface_2d(internal_geometry)

    def calc_union(self, other_polygon: Polygon2D) -> Union[EmptyGeometry2D, Polygon2D, MultiPolygon2D]:
        other_polygon_shapely = _ShapelyUtils.convert_polygon2d_to_shapely(other_polygon)
        if not other_polygon_shapely.is_valid or not self._shapely_obj.is_valid:
            raise InvalidGeometryException("Problem with internal geometry, not able to apply union")
        internal_geometry = self._shapely_obj.union(other_polygon_shapely)
        return _ShapelyUtils.convert_shapely_to_surface_2d(internal_geometry)

    def __str__(self):
        return self.type + [p.__str__() for p in self.points].__str__()

    def __eq__(self, other):
        return _ShapelyPolygon2D.is_approximately_equal_by_symmetric_difference(self, other)

    @staticmethod
    def is_approximately_equal_by_symmetric_difference(polygon1: Polygon2D, polygon2: Polygon2D,
                                                       epsilon_equal_area: float = EPSILON_FOR_EQUAL_AREA) -> bool:
        return polygon1.calc_difference(polygon2).calc_area() < epsilon_equal_area and \
               polygon2.calc_difference(polygon1).calc_area() < epsilon_equal_area


class _ShapelyMultiPolygon2D(_ShapelyGeometry, MultiPolygon2D):

    def __init__(self, polygons: List[Polygon2D]):
        super().__init__(MultiPolygon([_ShapelyUtils.convert_polygon2d_to_shapely(polygon) for polygon in polygons]))

    @property
    def _shapely_obj(self) -> MultiPolygon:
        return super()._shapely_obj

    def to_polygons(self) -> List[Polygon2D]:
        return [_ShapelyUtils.convert_shapely_to_polygon_2d(polygon) for polygon in list(self._shapely_obj)]

    def calc_area(self) -> float:
        return self._shapely_obj.area

    def __contains__(self, other_polygonal_geometry: [Polygon2D, MultiPolygon2D]) -> bool:
        if isinstance(other_polygonal_geometry, Polygon2D):
            return other_polygonal_geometry in self.to_polygons()
        return all([self.__contains__(polygon) for polygon in other_polygonal_geometry.to_polygons()])

    def __eq__(self, other_polygonal_geometry: [Polygon2D, MultiPolygon2D]):
        if isinstance(other_polygonal_geometry, Polygon2D):
            return other_polygonal_geometry in self
        return self in other_polygonal_geometry.to_polygons() and other_polygonal_geometry in self.to_polygons()

    def __str__(self):
        return self.type + [polygon.__str__ for polygon in self.to_polygons()].__str__()


class _ShapelyUtils:

    @staticmethod
    def convert_polygon2d_to_shapely(polygon: Polygon2D) -> Polygon:
        return Polygon(GeometryUtils.convert_points_list_to_xy_array(polygon.points))

    @staticmethod
    def convert_linear_ring2d_to_shapely(linear_ring: LinearRing2D) -> LinearRing:
        return LinearRing(GeometryUtils.convert_points_list_to_xy_array(linear_ring.points))

    @staticmethod
    def convert_line_string2d_to_shapely(line_string: LineString2D) -> LineString:
        return LineString(GeometryUtils.convert_points_list_to_xy_array(line_string.points))

    @staticmethod
    def convert_point2d_to_shapely(point: Point2D) -> Point:
        return Point(point.x, point.y)

    @staticmethod
    def convert_shapely_to_point_2d(point: Point) -> Point2D:
        return _ShapelyPoint2D(point.x, point.y)

    @staticmethod
    def convert_shapely_to_linear_ring_2d(linear_ring: LinearRing) -> LinearRing2D:
        return _ShapelyLinearRing2D(GeometryUtils.convert_xy_array_to_points_list(linear_ring.xy))

    @staticmethod
    def convert_shapely_to_polygon_2d(polygon: Polygon) -> Polygon2D:
        x_array, y_array = polygon.exterior.xy
        points_list_shapely = GeometryUtils.convert_xy_separate_arrays_to_points_list(x_array, y_array)
        return _ShapelyPolygon2D(points_list_shapely)

    @staticmethod
    def convert_shapely_to_multipolygon_2d(multipolygon: MultiPolygon) -> MultiPolygon2D:
        return _ShapelyMultiPolygon2D(
            [_ShapelyUtils.convert_shapely_to_polygon_2d(polygon) for polygon in multipolygon])

    @staticmethod
    def convert_shapely_to_surface_2d(internal_shapely_geometry: BaseGeometry) -> Union[
        EmptyGeometry2D, Polygon2D, MultiPolygon2D]:
        if internal_shapely_geometry.is_empty:
            return _ShapelyEmptyGeometry()
        if isinstance(internal_shapely_geometry, MultiPolygon):
            return _ShapelyUtils.convert_shapely_to_multipolygon_2d(internal_shapely_geometry)
        if isinstance(internal_shapely_geometry, Polygon):
            return _ShapelyUtils.convert_shapely_to_polygon_2d(internal_shapely_geometry)
        return _ShapelyEmptyGeometry()


class NonShapelyNativeGeometry(Exception):
    """
    Given operations requiring Shapely Geometry, an exception defining a non-shapely geometry will be used to validate.
    """
    pass


class NonPolygonalResult(Exception):
    """
    Given geometric operation the result is non polygonal.
    """
    pass


class InvalidGeometryException(Exception):
    """
    Invalid Geometry can't undergo difference/union/intersection operations, otherwise internal shapely package will break
    """
    pass
