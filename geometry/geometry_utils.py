from typing import Tuple, List, Iterator

from geometry.geo2d import Point2D


class GeometryUtils:

    @staticmethod
    def convert_xy_array_to_points_list(xy_array: Iterator[Tuple[float, float]]) -> List[Point2D]:
        from geometry.geo_factory import create_point_2d
        return [create_point_2d(xy[0], xy[1]) for xy in xy_array]

    @staticmethod
    def convert_xy_separate_arrays_to_points_list(x_array: List[float], y_array: List[float]) -> List[Point2D]:
        return GeometryUtils.convert_xy_array_to_points_list(zip(x_array, y_array))

    @staticmethod
    def convert_points_list_to_xy_array(points: List[Point2D]) -> List[Tuple[float, float]]:
        return [(p.x, p.y) for p in points]
