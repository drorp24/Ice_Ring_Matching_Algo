from itertools import repeat
from typing import List

from attr import dataclass
import numpy as np
import math

from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle
from grid.azimuth_options import AzimuthOptions
from grid.cell_data import  EnvelopeCellData
from grid.grid_location import GridLocationServices, GridLocation
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer


# class BaseGridLocation(ABC):
#
#     @abstractmethod
#     def __add__(self, other):
#         raise NotImplementedError()
#
#     @abstractmethod
#     def __sub__(self, other):
#         raise NotImplementedError()
#
#
# class GridLocation(BaseGridLocation):
#     def __init__(self, row: int, column: int):
#         self._row = row
#         self._column = column
#
#     @property
#     def row(self) -> int:
#         return self._row
#
#     @property
#     def column(self) -> int:
#         return self._column
#
#     @property
#     def location(self) -> np.array:
#         return np.array(self.row, self.column)
#
#     def __add__(self, other):
#         return GridLocation(self.row + other.row, self.column + other.column)
#
#     def __sub__(self, other):
#         return GridLocation(self.row - other.row, self.column - other.column)
#
#
# class NoneGridLocation(BaseGridLocation):
#     def __init__(self):
#         super().__init__(None, None)
#
#     def __add__(self, other):
#         return self
#
#     def __sub__(self, other):
#         return self
#
#
# class GridLocations:
#     def __init__(self, grid_locations: List[GridLocation]):
#         self._grid_locations = grid_locations
#
#     def append(self, value):
#         self._grid_locations.append(value)
#
#     def extend(self, other_grid_locations: List[GridLocation]):
#         self._grid_locations.extend(other_grid_locations)
#
#     def calc_average(self) -> GridLocation:
#         rows_values = []
#         columns_values = []
#
#         for grid_location in self._grid_locations:
#             rows_values.append(grid_location.row)
#             columns_values.append(grid_location.column)
#
#         return GridLocation(math.floor(np.mean(rows_values)),
#                             math.floor(np.mean(columns_values)))
#

@dataclass
class Cell:
    location: GridLocation


@dataclass
class EnvelopeCell(Cell):
    drone_azimuth: Angle


class CellServices:
    ANGLE_DELTA_COST = 10

    @staticmethod
    def get_distance(cell1: EnvelopeCell, cell2: EnvelopeCell) -> float:
        angle_delta = cell1.drone_azimuth.calc_abs_difference(cell2.drone_azimuth)
        dist = np.linalg.norm(cell1.location.location - cell2.location.location)
        angle_delta_cost = (math.cos(angle_delta.in_radians()) - 1)/-2
        return dist + CellServices.ANGLE_DELTA_COST / (dist+1) * angle_delta_cost


class DeliveryRequestEnvelopeCellsDict:
    def __init__(self, envelope_cells: List[EnvelopeCell]):
        pass
        # self._dict =


class DeliveryRequestEnvelopeCells:
    def __init__(self, slides_container: SlidesContainer, delivery_request: DeliveryRequest):
        self._slides_container = slides_container
        # self._delivery_request_envelope_cells = [_AzimuthOptions]

        map(DeliveryRequestEnvelopeCells._get_delivery_request_envelope_cells, delivery_request.delivery_options)

    @staticmethod
    def _get_delivery_request_envelope_cells(slides_container: SlidesContainer, delivery_option: DeliveryOption) -> \
            List[EnvelopeCell]:
        average_location = list(map(GridLocationServices.calc_average, list(zip(*(
            list(map(DeliveryRequestEnvelopeCells._scale_grid_locations, repeat(slides_container),
                     delivery_option.package_delivery_plans)))))))

        return list(map(EnvelopeCell, average_location,
                        list(map(EnvelopeCellData, AzimuthOptions(slides_container.get_drone_azimuth_resolution).values,
                                 []))))

    @staticmethod
    def _scale_grid_locations(slides_container: SlidesContainer, package_delivery_plan: PackageDeliveryPlan) -> List[
        GridLocation]:
        drop_point_grid_location = GridService.get_grid_location(package_delivery_plan.drop_point,
                                                                 slides_container.get_drone_azimuth_resolution)

        return list(map(sum, repeat(drop_point_grid_location),
                        map(DeliveryRequestEnvelopeCells._get_envelope_location, repeat(slides_container),
                            repeat(package_delivery_plan.package_type),
                            AzimuthOptions(slides_container.get_drone_azimuth_resolution).values,
                            map(DeliveryRequestEnvelopeCells._get_drop_azimuth,
                                AzimuthOptions(slides_container.get_drone_azimuth_resolution).values),
                            )))

    @staticmethod
    def _get_envelope_location(slides_container: SlidesContainer, package_type: PackageType,
                               drone_azimuth: Angle,
                               drop_azimuth: Angle) -> GridLocation:
        return slides_container.get_envelope_location(drone_azimuth, drop_azimuth,
                                                      package_type)

    @staticmethod
    def _get_drop_azimuth(drone_azimuth: Angle, drop_azimuth: Angle) -> Angle:
        return drop_azimuth if None else (drone_azimuth, drone_azimuth)
