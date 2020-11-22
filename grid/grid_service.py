import math
from typing import List

from optional import Optional

from geometry.geo2d import Point2D, EmptyGeometry2D, Polygon2D
from geometry.geo_factory import create_point_2d
from geometry.polygon_utils import PolygonUtils
from grid.grid_location import GridLocation


class GridService:

    @staticmethod
    def get_grid_location(point: Point2D, cell_resolution: int) -> GridLocation:
        return GridLocation(math.floor(point.x / cell_resolution), math.floor(point.y / cell_resolution))

    @staticmethod
    def get_polygon_centroid_grid_location(polygon: Polygon2D, cell_resolution: int) -> GridLocation:
        return GridService.get_grid_location(polygon.centroid, cell_resolution)

    @staticmethod
    def scale_to_grid(drop_point_grid_location: GridLocation, envelope_grid_location: Optional.of(GridLocation)) -> \
            Optional.of(GridLocation):

        scale_to_grid_location = drop_point_grid_location + envelope_grid_location
        return scale_to_grid_location if scale_to_grid_location != drop_point_grid_location else Optional.empty()
