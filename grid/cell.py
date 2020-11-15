from itertools import repeat
from typing import List

from attr import dataclass

from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import NoneAngle, BaseAngle
from grid.azimuth_options import AzimuthOptions
from grid.cell_data import CellData, EnvelopeCellData
from grid.grid_location import GridLocationServices, GridLocation
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer


@dataclass
class Cell:
    location: GridLocation
    data: CellData


@dataclass
class EnvelopeCell(Cell):
    data: EnvelopeCellData


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
    def _get_envelope_location(self, slides_container: SlidesContainer, package_type: PackageType,
                               drone_azimuth: BaseAngle,
                               drop_azimuth: BaseAngle) -> GridLocation:
        return slides_container.get_envelope_location(drone_azimuth, drop_azimuth,
                                                      package_type)

    @staticmethod
    def _get_drop_azimuth(drone_azimuth: BaseAngle, drop_azimuth: BaseAngle) -> BaseAngle:
        return drop_azimuth if not isinstance(drop_azimuth,
                                              NoneAngle) else (drone_azimuth, drone_azimuth)
