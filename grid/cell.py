import math
from abc import ABC, abstractmethod
from typing import List

import numpy as np
from attr import dataclass

from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import NoneAngle, Angle
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer
from params import MAX_AZIMUTH_ANGLE, MIN_AZIMUTH_ANGLE


class BaseGridLocation(ABC):

    @abstractmethod
    def __add__(self, other):
        raise NotImplementedError()

    @abstractmethod
    def __sub__(self, other):
        raise NotImplementedError()


class GridLocation(BaseGridLocation):
    def __init__(self, row: int, column: int):
        self._row = row
        self._column = column

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    @property
    def location(self) -> np.array:
        return np.array(self.row, self.column)

    def __add__(self, other):
        return GridLocation(self.row + other.row, self.column + other.column)

    def __sub__(self, other):
        return GridLocation(self.row - other.row, self.column - other.column)


class NoneGridLocation(BaseGridLocation):
    def __init__(self):
        super().__init__(None, None)

    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self


class GridLocations:
    def __init__(self, grid_locations: List[GridLocation]):
        self._grid_locations = grid_locations

    def append(self, value):
        self._grid_locations.append(value)

    def extend(self, other_grid_locations: List[GridLocation]):
        self._grid_locations.extend(other_grid_locations)

    def calc_average(self) -> GridLocation:
        rows_values = []
        columns_values = []

        for grid_location in self._grid_locations:
            rows_values.append(grid_location.row)
            columns_values.append(grid_location.column)

        return GridLocation(math.floor(np.mean(rows_values)),
                            math.floor(np.mean(columns_values)))


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


class _AzimuthOptions:

    def __init__(self, azimuth_resolution: int):
        azimuth_options = np.arange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE,
                                    MAX_AZIMUTH_ANGLE / azimuth_resolution)

        self._dict = {key: GridLocations for key in azimuth_options}

    @property
    def dict(self) -> dict:
        return self._dict

    def __getitem__(self, key) -> GridLocations:
        return self._dict[key]

    def append(self, key, value: GridLocation):
        self._dict[key].append(value)

    def keys(self) -> [int]:
        return self._dict.keys()

    def extend(self, other):
        for key in self.keys():
            grid_locations = self._dict[key]
            grid_locations.extend(other[key])
            self._dict[key] = grid_locations


class PackageDeliveryPlanEnvelopeCells:
    def __init__(self, slides_container: SlidesContainer, package_delivery_plan: PackageDeliveryPlan):
        self._drone_azimuth_options = _AzimuthOptions(slides_container.get_drone_azimuth_resolution)

        for drone_azimuth in self._drone_azimuth_options.keys():
            drop_azimuth = package_delivery_plan.azimuth if not isinstance(package_delivery_plan.azimuth,
                                                                           NoneAngle) else drone_azimuth

            envelope_grid_location = slides_container.get_envelope_location(drone_azimuth, drop_azimuth,
                                                                            package_delivery_plan.package_type)

            drop_point_grid_location = GridService.get_grid_location(package_delivery_plan.drop_point,
                                                                     slides_container.get_drone_azimuth_resolution)

            scale_grid_location = envelope_grid_location + drop_point_grid_location

            self._drone_azimuth_options.append(key=drone_azimuth, value=scale_grid_location)

    def azimuth_options(self) -> _AzimuthOptions:
        return self._drone_azimuth_options


class CustomerDeliveryEnvelopeCells:
    def __init__(self, slides_container: SlidesContainer, customer_delivery: CustomerDelivery):
        self._drone_azimuth_options = _AzimuthOptions(slides_container.get_drone_azimuth_resolution)

        for package_delivery_plan in customer_delivery.package_delivery_plans:
            package_delivery_plan_envelope_cells = PackageDeliveryPlanEnvelopeCells(slides_container,
                                                                                    package_delivery_plan)

            self._drone_azimuth_options.extend(package_delivery_plan_envelope_cells.azimuth_options())

    def azimuth_options(self) -> _AzimuthOptions:
        return self._drone_azimuth_options


class DeliveryOptionsEnvelopeCells:

    def __init__(self, slides_container: SlidesContainer, delivery_option: DeliveryOption):
        self._drone_azimuth_options = _AzimuthOptions(slides_container.get_drone_azimuth_resolution)
        self._drone_azimuth_options_average = _AzimuthOptions(slides_container.get_drone_azimuth_resolution)

        for customer_delivery in delivery_option.customer_deliveries:
            customer_delivery_envelope_cells = CustomerDeliveryEnvelopeCells(slides_container,
                                                                             customer_delivery)

            self._drone_azimuth_options.extend(customer_delivery_envelope_cells.azimuth_options())

        self._calc_azimuth_options_average()

    def azimuth_options_average(self) -> _AzimuthOptions:
        return self._drone_azimuth_options_average

    def _calc_azimuth_options_average(self):
        for key in self._drone_azimuth_options.keys():
            self._drone_azimuth_options_average.append(key=key, value=self._drone_azimuth_options[key].calc_average())


class DeliveryRequestEnvelopeCells:
    def __init__(self, slides_container: SlidesContainer, delivery_request: DeliveryRequest):
        self._delivery_request_envelope_cells = [_AzimuthOptions]
        for delivery_option in delivery_request.delivery_options:
            delivery_option_envelope_cells = DeliveryOptionsEnvelopeCells(slides_container,
                                                                          delivery_option)
            self._delivery_request_envelope_cells.append(delivery_option_envelope_cells.azimuth_options_average())


    @property
    def delivery_request_envelope_cells(self) -> [_AzimuthOptions]:
        return self._delivery_request_envelope_cells

#
# class DeliveryRequestEnvelopeCellsOld:
#
#     def __init__(self, slides_container: SlidesContainer, delivery_request: DeliveryRequest):
#         for delivery_option in delivery_request.delivery_options:
#
#             drone_azimuth_options = np.arange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE,
#                                               MAX_AZIMUTH_ANGLE / slide_container.get_drone_azimuth_resolution)
#             delivery_option_envelope_cell_dict = {drone_azimuth: [] for drone_azimuth in drone_azimuth_options}
#             for customer_delivery in delivery_option.customer_deliveries:
#                 for package_delivery_plan in customer_delivery.package_delivery_plans:
#                     for drone_azimuth in drone_azimuth_options:
#                         drop_azimuth = package_delivery_plan.drop_azimuth if \
#                             package_delivery_plan.drop_azimuth \
#                             != -1 \
#                             else package_delivery_plan.drone_azimuth
#
#                         grid_location = slide_container.get_envelope_location(drone_azimuth, drop_azimuth,
#                                                                               package_delivery_plan.package_type)
#
#                         # get drop point as point on the grid
#
#                         # add results to grid location
#
#                         grid_location_2 = GridLocation(grid_location.row +)
#                         delivery_option_envelope_cell_dict[drone_azimuth].append = grid_location
#
#                         # calc average to x and y separately
#
#                         # append delivery_option_envelope_cell_dict to delivery option
#                         delivery_options_envelope_cells.append(delivery_option_envelope_cells)
#
#                         # create Grid  - init with DeliveryRequests   and convert to
#                         # DeliveryRequestEnvelopeCells
#                         # hold dict by DR id
#
#                         # Grid - implements GetDIst( DR1, DR 2)
#
#                         # getdists - return number
#                         # calc all strike combination and save the closet strikes
#
#
# def calc_envelope_cells(self):
#
#
# def __eq__(self, other):
#     return (self.location == other.location) and \
#            (self.data == other.data)
