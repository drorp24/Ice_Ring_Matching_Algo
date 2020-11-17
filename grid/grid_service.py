import math
from typing import List

from optional import Optional

from geometry.geo2d import Point2D, EmptyGeometry2D, Polygon2D
from geometry.geo_factory import create_point_2d
from geometry.polygon_utils import PolygonUtils
from grid.cell import GridLocation


class GridService:

    @staticmethod
    def polygon_to_grid_cells(polygon: Polygon2D, cell_resolution: int, cell_ratio_required: float) -> \
            Optional.of[List[GridLocation]]:

        if isinstance(polygon, EmptyGeometry2D):
            return Optional.empty()

        required_area = PolygonUtils.convert_ratio_to_required_area(cell_resolution, cell_ratio_required)
        splitter_polygons = PolygonUtils.split_polygon(polygon, box_resolution=cell_resolution,
                                                       required_area=required_area)
        locations = []
        for split_polygon in splitter_polygons:
            bbox = split_polygon.bbox
            min_x, min_y = bbox.min_x, bbox.min_y
            min_x_y_point = create_point_2d(math.floor(min_x / cell_resolution),
                                            math.floor(min_y / cell_resolution))
            locations.append(GridService.get_grid_location(min_x_y_point, cell_resolution))

        return locations

    @staticmethod
    def get_grid_location(point: Point2D, cell_resolution: int) -> GridLocation:
        return GridLocation(math.floor(point.x / cell_resolution), math.floor(point.y / cell_resolution))

    @staticmethod
    def get_polygon_centroid_grid_location(polygon: Polygon2D, cell_resolution: int) -> GridLocation:
        return GridService.get_grid_location(polygon.centroid, cell_resolution)
