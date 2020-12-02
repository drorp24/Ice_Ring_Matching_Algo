from itertools import repeat
from typing import List

from optional import Optional

from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle
from grid.azimuth_options import AzimuthOptions
from grid.grid_cell import EnvelopeGridCell
from grid.grid_cell_services import GridCellServices
from grid.grid_location import GridLocation, GridLocationServices
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer


class PotentialEnvelope:
    def __init__(self, envelope_cells: List[EnvelopeGridCell]):
        self._envelope_cells = {envelope_cell.drone_azimuth: envelope_cell for envelope_cell in envelope_cells}

    @property
    def envelope_cells(self) -> dict:
        return self._envelope_cells

    def keys(self) -> [Angle]:
        return list(self._envelope_cells.keys())

    def __getitem__(self, drone_azimuth: Angle) -> EnvelopeGridCell:
        return self._envelope_cells[drone_azimuth]

    def values(self) -> [EnvelopeGridCell]:
        return list(self._envelope_cells.values())


class DeliveryRequestPotentialEnvelope:
    def __init__(self, slides_container: SlidesContainer, delivery_request: DeliveryRequest):
        self._delivery_options_cells = list(map(PotentialEnvelope, list(
            map(DeliveryRequestPotentialEnvelope._get_delivery_request_envelope_cells, repeat(slides_container),
                delivery_request.delivery_options))))

    @property
    def delivery_options_cells(self) -> List[PotentialEnvelope]:
        return self._delivery_options_cells

    @staticmethod
    def _get_delivery_request_envelope_cells(slides_container: SlidesContainer, delivery_option: DeliveryOption) -> \
            List[EnvelopeGridCell]:
        scale_grid_locations = list(
            map(DeliveryRequestPotentialEnvelope._get_scaled_grid_locations, repeat(slides_container),
                delivery_option.package_delivery_plans))

        average_locations = list(
            map(GridLocationServices.calc_average, list(zip(*scale_grid_locations))))

        average_package_delivery_list = list(
            map(DeliveryRequestPotentialEnvelope._get_package_delivery_list, list(
                map(GridLocationServices.get_not_empty_indices, list(zip(*scale_grid_locations)))),
                repeat(delivery_option.package_delivery_plans)))

        return list(map(EnvelopeGridCell, average_locations,
                        AzimuthOptions(slides_container.get_drone_azimuth_resolution).values,
                        average_package_delivery_list))

    @staticmethod
    def _get_package_delivery_list(indices_to_calc: List[int],
                                   package_delivery_plans: List[PackageDeliveryPlan]) -> List[PackageDeliveryPlan]:
        return list(map(package_delivery_plans.__getitem__, indices_to_calc))

    @staticmethod
    def _get_scaled_grid_locations(slides_container: SlidesContainer,
                                   package_delivery_plan: PackageDeliveryPlan) -> [Optional.of(GridLocation)]:
        drop_point_grid_location = GridService.get_grid_location(package_delivery_plan.drop_point,
                                                                 slides_container.cell_width_resolution,
                                                                 slides_container.cell_height_resolution)

        scale_to_grid = list(map(GridService.scale_to_grid, repeat(drop_point_grid_location),
                                 DeliveryRequestPotentialEnvelope._get_envelope_location_values(slides_container,
                                                                                                package_delivery_plan)))

        return scale_to_grid

    @staticmethod
    def _get_envelope_location_values(slides_container: SlidesContainer,
                                      package_delivery_plan: PackageDeliveryPlan):
        return list(map(slides_container.get_envelope_location,
                        AzimuthOptions(slides_container.get_drone_azimuth_resolution).values,
                        DeliveryRequestPotentialEnvelope._get_drop_azimuth_values(slides_container, package_delivery_plan),
                        repeat(package_delivery_plan.package_type))
                    )

    @staticmethod
    def _get_drop_azimuth_values(slides_container: SlidesContainer,
                                 package_delivery_plan: PackageDeliveryPlan):
        return list(map(GridCellServices.get_drop_azimuth,
                        AzimuthOptions(
                            slides_container.get_drone_azimuth_resolution).values,
                        repeat(package_delivery_plan.azimuth),
                        repeat(package_delivery_plan.pitch)
                        ))
