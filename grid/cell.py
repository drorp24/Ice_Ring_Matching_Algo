import math
from itertools import repeat
from typing import List, KeysView, ValuesView

import numpy as np
from attr import dataclass

from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle
from grid.azimuth_options import AzimuthOptions
from grid.grid_location import GridLocationServices, GridLocation
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer
from params import MAX_PITCH_DEGREES


@dataclass
class Cell:
    location: GridLocation


@dataclass
class EnvelopeCell(Cell):
    drone_azimuth: Angle
    package_delivery_plan_ids: List[int]


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
        average_location = list(map(GridLocationServices.calc_average, list(zip(*(
            list(map(DeliveryRequestEnvelopeCells._scale_grid_locations, repeat(slides_container),
                     delivery_option.package_delivery_plans)))))))

        return list(map(EnvelopeCell, average_location,
                        AzimuthOptions(slides_container.get_drone_azimuth_resolution).values))

    @staticmethod
    def _scale_grid_locations(slides_container: SlidesContainer,
                              package_delivery_plan: PackageDeliveryPlan) -> List[GridLocation]:
        drop_point_grid_location = GridService.get_grid_location(package_delivery_plan.drop_point,
                                                                 slides_container.get_drone_azimuth_resolution)

        return list(map(sum, repeat(drop_point_grid_location),
                        map(DeliveryRequestEnvelopeCells._get_envelope_location, repeat(slides_container),
                            repeat(package_delivery_plan.package_type),
                            AzimuthOptions(slides_container.get_drone_azimuth_resolution).values,
                            map(DeliveryRequestEnvelopeCells._get_drop_azimuth,
                                AzimuthOptions(slides_container.get_drone_azimuth_resolution).values),
                            repeat(package_delivery_plan.azimuth), repeat(package_delivery_plan.pitch)
                            )))

    @staticmethod
    def _get_envelope_location(slides_container: SlidesContainer, package_type: PackageType,
                               drone_azimuth: Angle,
                               drop_azimuth: Angle) -> GridLocation:
        return slides_container.get_envelope_location(drone_azimuth, drop_azimuth,
                                                      package_type)

    @staticmethod
    def _get_drop_azimuth(drone_azimuth: Angle, drop_azimuth: Angle, drop_pitch: Angle) -> Angle:
        return drop_azimuth if drop_pitch == MAX_PITCH_DEGREES else drone_azimuth
