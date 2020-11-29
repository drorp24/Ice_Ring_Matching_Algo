import math
from typing import List

import numpy as np

from geometry import geo_factory
from geometry.geo2d import Polygon2D, MultiPolygon2D


class PolygonUtils:
    MAX_ITERATION = 250

    @staticmethod
    def convert_ratio_to_required_area(box_resolution: int, box_ratio_required: float):
        return box_resolution ** 2 * box_ratio_required

    @staticmethod
    def convert_higher_value_in_resolution(value: float, resolution: int) -> int:
        return math.ceil(value / resolution) * resolution

    @staticmethod
    def convert_lower_value_in_resolution(value: float, resolution: int) -> int:
        return math.floor(value / resolution) * resolution

    @staticmethod
    def convert_nearest_value_in_resolution(value: float, resolution: int) -> int:
        return round(value / resolution) * resolution

    @staticmethod
    def split_polygon(polygon: Polygon2D, box_resolution: int, required_area: float) -> List[
        Polygon2D]:

        bounds = polygon.bbox
        min_x = math.floor(bounds.min_x / box_resolution) * box_resolution
        min_y = math.floor(bounds.min_y / box_resolution) * box_resolution
        max_x = math.ceil(bounds.max_x / box_resolution) * box_resolution
        max_y = math.ceil(bounds.max_y / box_resolution) * box_resolution

        #   TODO :  add max split check

        if max(max_x - min_x, max_y - min_y) <= box_resolution:
            return [polygon]

        boxes = [geo_factory.create_bbox(x, y, x + box_resolution, y + box_resolution) for x in
                 range(min_x, max_x, box_resolution) for y in np.arange(min_y, max_y, box_resolution)]
        result = []
        for bbox in boxes:

            internal_intersection = polygon.calc_intersection(bbox)

            area = internal_intersection.calc_area()
            if area < required_area:
                continue

            if isinstance(internal_intersection, Polygon2D):
                result.append(internal_intersection)
            elif isinstance(internal_intersection, MultiPolygon2D):
                result.extend(internal_intersection)

        return result
