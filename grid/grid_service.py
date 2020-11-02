import math

from geometry.geo2d import Point2D, Bbox2D
from grid.cell import GridLocation


class GridService:

    # def __init__(self, area: Bbox2D, resolution: int):
    #     # _grid = numpy.zeros((ceil((area[0][1] - area[0][0])/resolution), ceil((area[1][1] - area[1][0])/resolution)))
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
    def get_grid_location(self, point: Point2D, cell_resolution: int) -> GridLocation:
        return GridLocation(math.floor(point.x / cell_resolution), math.floor(point.y / cell_resolution))

    # def _get_location(self, grid_indecies: [int, int]) -> [int, int]:
    #     pass
