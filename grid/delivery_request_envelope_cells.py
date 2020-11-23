from itertools import repeat
from typing import List

from optional import Optional

from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package_delivery_plan import PackageDeliveryPlan, PackageDeliveryPlanList
from common.math.angle import Angle
from grid.azimuth_options import AzimuthOptions
from grid.cell import EnvelopeCell
from grid.cell_services import CellServices
from grid.grid_location import GridLocation, GridLocationServices
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer


class DeliveryRequestEnvelopeCellsDict:
    def __init__(self, envelope_cells: List[EnvelopeCell]):
        self._dict = {}
        for envelope_cell in envelope_cells:
            self._dict[envelope_cell.drone_azimuth] = envelope_cell

    @property
    def dict(self) -> dict:
        return self._dict

    def keys(self) -> [Angle]:
        return list(self._dict.keys())

    def __getitem__(self, drone_azimuth: Angle) -> EnvelopeCell:
        return self._dict[drone_azimuth]

    def values(self) -> [EnvelopeCell]:
        return list(self._dict.values())


class DeliveryRequestEnvelopeCells:
    def __init__(self, slides_container: SlidesContainer, delivery_request: DeliveryRequest):
        self._cells = list(map(DeliveryRequestEnvelopeCellsDict, list(
            map(DeliveryRequestEnvelopeCells._get_delivery_request_envelope_cells, repeat(slides_container),
                delivery_request.delivery_options))))

    @property
    def cells(self) -> List[DeliveryRequestEnvelopeCellsDict]:
        return self._cells

    @staticmethod
    def _get_delivery_request_envelope_cells(slides_container: SlidesContainer, delivery_option: DeliveryOption) -> \
            List[EnvelopeCell]:
        scale_grid_locations = list(
            map(DeliveryRequestEnvelopeCells._get_scaled_grid_locations, repeat(slides_container),
                delivery_option.package_delivery_plans))

        average_locations = list(
            map(GridLocationServices.calc_average, list(zip(*scale_grid_locations))))

        average_package_delivery_list = list(
            map(DeliveryRequestEnvelopeCells._get_package_delivery_list, list(
                map(GridLocationServices.get_not_empty_indices, list(zip(*scale_grid_locations)))),
                repeat(delivery_option.package_delivery_plans)))

        return list(map(EnvelopeCell, average_locations,
                        AzimuthOptions(slides_container.get_drone_azimuth_resolution).values,
                        average_package_delivery_list))

    @staticmethod
    def _get_package_delivery_list(indices_to_calc: List[int],
                                   package_delivery_plans: List[PackageDeliveryPlan]) -> PackageDeliveryPlanList:
        return PackageDeliveryPlanList(list(map(package_delivery_plans.__getitem__, indices_to_calc)))

    @staticmethod
    def _get_scaled_grid_locations(slides_container: SlidesContainer,
                                   package_delivery_plan: PackageDeliveryPlan) -> [Optional.of(GridLocation)]:
        drop_point_grid_location = GridService.get_grid_location(package_delivery_plan.drop_point,
                                                                 slides_container.get_drone_azimuth_resolution)

        scale_to_grid = list(map(GridService.scale_to_grid, repeat(drop_point_grid_location),
                                 list(map(slides_container.get_envelope_location,
                                          AzimuthOptions(
                                              slides_container.get_drone_azimuth_resolution).values,
                                          list(map(CellServices.get_drop_azimuth,
                                                   AzimuthOptions(
                                                       slides_container.get_drone_azimuth_resolution).values,
                                                   repeat(package_delivery_plan.azimuth),
                                                   repeat(package_delivery_plan.pitch)
                                                   )),
                                          repeat(package_delivery_plan.package_type))
                                      )))

        return scale_to_grid
