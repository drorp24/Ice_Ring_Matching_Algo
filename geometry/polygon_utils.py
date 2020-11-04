import math
from typing import List

import numpy as np

from geometry import geo_factory
from geometry.geo2d import Polygon2D, MultiPolygon2D
from grid.cell import GridLocation


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

        # if count == PolygonUtils.MAX_ITERATION: todo add max split check
        #     raise ValueError("split polygon has been reached to the maximum number of recursions")

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

    @staticmethod
    def split_polygon_recursive(polygon: Polygon2D, box_resolution: int, required_area: float, count=0) -> List[
        Polygon2D]:

        bounds = polygon.bbox
        min_x = PolygonUtils.convert_lower_value_in_resolution(bounds.min_x, box_resolution)
        min_y = PolygonUtils.convert_lower_value_in_resolution(bounds.min_y, box_resolution)
        max_x = PolygonUtils.convert_higher_value_in_resolution(bounds.max_x, box_resolution)
        max_y = PolygonUtils.convert_higher_value_in_resolution(bounds.max_y, box_resolution)

        width = max_x - min_x
        height = max_y - min_y

        if count == PolygonUtils.MAX_ITERATION:
            raise ValueError("split polygon has been reached to the maximum number of recursions")

        if max(width, height) <= box_resolution:
            return [polygon]

        if height >= width:
            separator = PolygonUtils.convert_higher_value_in_resolution(min_y + height / 2, box_resolution)
            bbox_1 = geo_factory.create_bbox(min_x, min_y, max_x, separator)
            bbox_2 = geo_factory.create_bbox(min_x, separator, max_x, max_y)
        else:
            separator = PolygonUtils.convert_higher_value_in_resolution(min_x + width / 2, box_resolution)
            bbox_1 = geo_factory.create_bbox(min_x, min_y, separator, max_y)
            bbox_2 = geo_factory.create_bbox(separator, min_y, max_x, max_y)

        result = []
        for bbox in (bbox_1, bbox_2,):
            internal_intersection = polygon.calc_intersection(bbox)

            area = internal_intersection.calc_area()
            if area < required_area:
                continue

            if isinstance(internal_intersection, (Polygon2D, MultiPolygon2D)):
                result.extend(PolygonUtils.split_polygon_recursive(internal_intersection, box_resolution, required_area,
                                                                   count + 1))

        if count > 0:
            return result

        final_result = []
        for g in result:
            if isinstance(g, MultiPolygon2D):
                final_result.extend(g)
            else:
                final_result.append(g)
        return final_result

    @staticmethod
    def get_envelope_boundary(envelope_locations) -> List[GridLocation]:
        envelope_boundary_locations = []
        if not envelope_locations:
            return envelope_boundary_locations
        min_x = min([envelope_location.row for envelope_location in envelope_locations])
        max_x = max([envelope_location.row for envelope_location in envelope_locations])
        min_y = min([envelope_location.column for envelope_location in envelope_locations])
        max_y = max([envelope_location.column for envelope_location in envelope_locations])
        x_bounds = np.ones((max_x - min_x + 1, 2))
        x_bounds[:, 0] *= max_y
        x_bounds[:, 1] *= min_y
        y_bounds = np.ones((max_y - min_y + 1, 2))
        y_bounds[:, 0] *= max_x
        y_bounds[:, 1] *= min_x

        for location in envelope_locations:
            index = location.row - min_x
            x_bounds[index, 0] = min(x_bounds[index, 0], location.column)
            x_bounds[index, 1] = max(x_bounds[index, 1], location.column)

            index = location.column - min_y
            y_bounds[index, 0] = min(y_bounds[index, 0], location.row)
            y_bounds[index, 1] = max(y_bounds[index, 1], location.row)

        for x_index, x_bound in enumerate(x_bounds):
            envelope_boundary_locations.append(GridLocation(min_x + x_index, x_bound[0]))
            envelope_boundary_locations.append(GridLocation(min_x + x_index, x_bound[1]))

        for y_index, y_bound in enumerate(y_bounds):
            x_index = int(y_bound[0]) - min_x
            y_pos = min_y + y_index
            if x_bounds[x_index, 0] != y_pos and x_bounds[x_index, 1] != y_pos:
                envelope_boundary_locations.append(GridLocation(y_bound[0], y_pos))

            x_index = int(y_bound[1]) - min_x
            if x_bounds[x_index, 0] != y_pos and x_bounds[x_index, 1] != y_pos:
                envelope_boundary_locations.append(GridLocation(y_bound[1], y_pos))

        return envelope_boundary_locations
