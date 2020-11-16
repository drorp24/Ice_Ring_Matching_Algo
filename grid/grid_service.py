import math
from typing import List, Union

from geometry.geo2d import Point2D, EmptyGeometry2D, Polygon2D
from geometry.geo_factory import create_point_2d
from geometry.polygon_utils import PolygonUtils
from grid.cell import GridLocation
from grid.grid_location import NoneGridLocation


class GridService:

    # def __init__(self, area: Bbox2D, resolution: int):
    #     # _grid = numpy.zeros((ceil((area[0][1] - area[0][0])/resolution), ceil((area[1][1] - area[1][
    #     0])/resolution)))
    #     # _grid_position = [area[0][0], area[1][0]]
    #     # _x_length = ceil((area[0][1] - area[0][0]) / resolution)
    #     # _y_length = ceil((area[1][1] - area[1][0]) / resolution)
    #     self._area = area
    #     self._resolution = resolution
    #     # _grid_cells = {}
    #     # _deliveries_drop_envelops = {}
    #
    # # def add_delivery(self, delivery_request: DeliveryRequest):
    # #     for delivery_option in delivery_request.delivery_options:
    # #         for customer_delivery in delivery_option.customer_deliveries:
    # #             for package_delivery_plan in customer_delivery.package_delivery_plans:
    # #                 pass

    @staticmethod
    def polygon_to_grid_cells(polygon: Polygon2D, cell_resolution: int, cell_ratio_required: float) -> Union[
            List[GridLocation], NoneGridLocation]:

        if isinstance(polygon, EmptyGeometry2D):
            return NoneGridLocation()

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



