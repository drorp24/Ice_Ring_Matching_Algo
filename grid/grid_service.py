import math

from optional import Optional

from geometry.geo2d import Point2D, Polygon2D
from grid.grid_location import GridLocation


class GridService:

    @staticmethod
    def get_grid_location(point: Point2D, cell_width_resolution: float, cell_height_resolution: float) -> GridLocation:
        return GridLocation(math.floor(point.x / cell_width_resolution), math.floor(point.y / cell_height_resolution))

    @staticmethod
    def get_polygon_centroid_grid_location(polygon: Polygon2D,
                                           cell_width_resolution: float, cell_height_resolution: float) -> GridLocation:
        return GridService.get_grid_location(polygon.centroid(), cell_width_resolution, cell_height_resolution)

    @staticmethod
    def scale_to_grid(drop_point_grid_location: GridLocation, envelope_grid_location: Optional.of(GridLocation)) -> \
            Optional.of(GridLocation):
        return Optional.of(
            drop_point_grid_location + envelope_grid_location.get()) if not envelope_grid_location.is_empty() else \
            Optional.empty()
