from typing import Tuple, List, Iterator

from geometry.geo2d import Point2D, Polygon2D, MultiPolygon2D
from geometry.geo_factory import create_bbox


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


class PolygonUtils:
    MAX_ITERATION = 250

    @staticmethod
    def convert_ratio_to_required_area(box_resolution: int, box_ratio_required: float):
        return box_resolution ** 2 * box_ratio_required

    @staticmethod
    def split_polygon(polygon: Polygon2D, box_resolution: int, required_area: float, count=0) -> List[Polygon2D]:

        bounds = polygon.bbox
        width = bounds.max_x - bounds.min_x
        height = bounds.max_y - bounds.min_y

        if count == PolygonUtils.MAX_ITERATION:
            raise ValueError("split polygon has been reached to the maximum number of recursions")

        if max(width, height) <= box_resolution:
            return [polygon]

        if height >= width:
            bbox_1 = create_bbox(bounds.min_x, bounds.min_y, bounds.max_x, bounds.min_y + height / 2)
            bbox_2 = create_bbox(bounds.min_x, bounds.min_y + height / 2, bounds.max_x, bounds.max_y)
        else:
            bbox_1 = create_bbox(bounds.min_x, bounds.min_y, bounds.min_x + width / 2, bounds.max_y)
            bbox_2 = create_bbox(bounds.min_x + width / 2, bounds.min_y, bounds.max_x, bounds.max_y)

        result = []
        for bbox in (bbox_1, bbox_2,):
            internal_intersection = polygon.calc_intersection(bbox)

            area = internal_intersection.calc_area()
            if area < required_area:
                continue

            if isinstance(internal_intersection, (Polygon2D, MultiPolygon2D)):
                result.extend(PolygonUtils.split_polygon(internal_intersection, box_resolution, count + 1))

        if count > 0:
            return result

        final_result = []
        for g in result:
            if isinstance(g, MultiPolygon2D):
                final_result.extend(g)
            else:
                final_result.append(g)
        return final_result
