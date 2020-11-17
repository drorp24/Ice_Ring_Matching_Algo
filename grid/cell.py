import math
from itertools import repeat
from typing import List, KeysView, ValuesView

import numpy as np
from attr import dataclass
from optional import Optional

from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan, PackageDeliveryPlanList
from common.math.angle import Angle
from grid.azimuth_options import AzimuthOptions
from grid.grid_location import GridLocationServices, GridLocation
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer
from params import MAX_PITCH_DEGREES


@dataclass
class Cell:
    location: GridLocation


class EnvelopeCell(Cell):
    drone_azimuth: Angle
    package_delivery_plans: PackageDeliveryPlanList


class CellServices:
    ANGLE_DELTA_COST = 10

    @staticmethod
    def get_distance(cell1: EnvelopeCell, cell2: EnvelopeCell) -> float:
        angle_delta = cell1.drone_azimuth.calc_abs_difference(cell2.drone_azimuth)
        dist = np.linalg.norm(cell1.location - cell2.location)
        angle_delta_cost = (math.cos(angle_delta.radians) - 1) / -2
        return dist + CellServices.ANGLE_DELTA_COST / (dist + 1) * angle_delta_cost


class DeliveryRequestEnvelopeCellsDict:
    def __init__(self, envelope_cells: List[EnvelopeCell]):
        self._dict = {}
        for envelope_cell in envelope_cells:
            self._dict[envelope_cell.drone_azimuth] = envelope_cell

    @property
    def dict(self) -> dict:
        return self._dict

    def keys(self) -> KeysView[Angle]:
        return self._dict.keys()

    def get_envelope_cell(self, drone_azimuth: Angle) -> EnvelopeCell:
        return self._dict[drone_azimuth]

    def values(self) -> ValuesView[EnvelopeCell]:
        return self._dict.values()


class DeliveryRequestEnvelopeCells:
    def __init__(self, slides_container: SlidesContainer, delivery_request: DeliveryRequest):
        self._delivery_request_envelope_cells = list(map(DeliveryRequestEnvelopeCellsDict, list(
            map(DeliveryRequestEnvelopeCells._get_delivery_request_envelope_cells, repeat(slides_container),
                delivery_request.delivery_options))))

    @property
    def delivery_request_envelope_cells(self) -> List[DeliveryRequestEnvelopeCellsDict]:
        return self._delivery_request_envelope_cells

    @staticmethod
    def _get_delivery_request_envelope_cells(slides_container: SlidesContainer, delivery_option: DeliveryOption) -> \
            List[EnvelopeCell]:
        scale_grid_locations = list(
            map(DeliveryRequestEnvelopeCells._get_scaled_grid_locations, repeat(slides_container),
                delivery_option.package_delivery_plans))

        indices_to_calc_average = list(
            map(DeliveryRequestEnvelopeCells._get_indices_to_calc_average, list(zip(*scale_grid_locations))))

        average_locations = list(
            map(DeliveryRequestEnvelopeCells._calc_average, indices_to_calc_average, list(zip(*scale_grid_locations))))

        average_uuids = list(map(DeliveryRequestEnvelopeCells._get_average_uuids,
                                 repeat(delivery_option.package_delivery_plans), indices_to_calc_average))

        return list(map(EnvelopeCell, average_locations, average_uuids,
                        AzimuthOptions(slides_container.get_drone_azimuth_resolution).values))

    @staticmethod
    def _get_indices_to_calc_average(grid_locations: List[Optional.of(GridLocation)]) -> List[int]:
        return [index for index, grid_location in enumerate(grid_locations) if
                grid_location != Optional.empty()]

    @staticmethod
    def _calc_average(indices_to_calc: List[int], grid_locations: List[GridLocation]) -> GridLocation:
        return GridLocationServices.calc_average(list(map(grid_locations.__getitem__, indices_to_calc)))

    @staticmethod
    def _get_average_uuids(indices_to_calc: List[int],
                           package_delivery_plans: List[PackageDeliveryPlan]) -> PackageDeliveryPlanList:
        return PackageDeliveryPlanList(list(map(package_delivery_plans.__getitem__, indices_to_calc)))

    @staticmethod
    def _get_scaled_grid_locations(slides_container: SlidesContainer,
                                   package_delivery_plan: PackageDeliveryPlan) -> List[Optional.of(GridLocation)]:
        drop_point_grid_location = GridService.get_grid_location(package_delivery_plan.drop_point,
                                                                 slides_container.get_drone_azimuth_resolution)

        return list(map(DeliveryRequestEnvelopeCells._scale_to_grid, repeat(drop_point_grid_location),
                        map(DeliveryRequestEnvelopeCells._get_envelope_location, repeat(slides_container),
                            repeat(package_delivery_plan.package_type),
                            AzimuthOptions(slides_container.get_drone_azimuth_resolution).values,
                            map(DeliveryRequestEnvelopeCells._get_drop_azimuth,
                                AzimuthOptions(slides_container.get_drone_azimuth_resolution).values),
                            repeat(package_delivery_plan.azimuth), repeat(package_delivery_plan.pitch)
                            )))

    @staticmethod
    def _scale_to_grid(drop_point_grid_location: GridLocation, envelope_grid_location: GridLocation) -> Optional.of(
        GridLocation):
        return Optional.of(envelope_grid_location).if_present(
            drop_point_grid_location + envelope_grid_location).or_else(Optional.empty())

    @staticmethod
    def _get_envelope_location(slides_container: SlidesContainer, package_type: PackageType,
                               drone_azimuth: Angle,
                               drop_azimuth: Angle) -> Optional.of(GridLocation):
        return slides_container.get_envelope_location(drone_azimuth, drop_azimuth,
                                                      package_type)

    @staticmethod
    def _get_drop_azimuth(drone_azimuth: Angle, drop_azimuth: Angle, drop_pitch: Angle) -> Angle:
        return drop_azimuth if drop_pitch == MAX_PITCH_DEGREES else drone_azimuth
