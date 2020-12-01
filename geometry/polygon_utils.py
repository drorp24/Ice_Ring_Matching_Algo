from typing import List

import numpy as np

from geometry import geo_factory
from geometry.geo2d import Polygon2D, MultiPolygon2D
from grid.grid_geometry_utils import convert_lower_value_in_resolution, convert_higher_value_in_resolution


class PolygonUtils:
    MAX_ITERATION = 250

    @staticmethod
    def split_polygon(polygon: Polygon2D, box_resolution: int, required_area: float) -> List[
        Polygon2D]:

        bounds = polygon.bbox
        min_x = convert_lower_value_in_resolution(bounds.min_x, box_resolution)
        min_y = convert_lower_value_in_resolution(bounds.min_y, box_resolution)
        max_x = convert_higher_value_in_resolution(bounds.max_x, box_resolution)
        max_y = convert_higher_value_in_resolution(bounds.max_y, box_resolution)

        #   TODO :  add max split check if needed

        if max(max_x - min_x, max_y - min_y) <= box_resolution:
            return [polygon]

        boxes = [geo_factory.create_bbox(x, y, x + box_resolution, y + box_resolution) for x in
                 range(min_x, max_x, box_resolution) for y in np.arange(min_y, max_y, box_resolution)]
        return PolygonUtils._get_polygon_boxes(boxes, polygon, required_area)

    @staticmethod
    def _get_polygon_boxes(boxes, polygon, required_area):
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
