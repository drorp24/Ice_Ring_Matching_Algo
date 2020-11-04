from typing import List, Union

from common.entities.package import PackageType
from common.math.angle import Angle
from geometry.geo2d import EmptyGeometry2D, Polygon2D
from geometry.geo_factory import create_point_2d
from geometry.polygon_utils import PolygonUtils
from grid.cell import GridLocation, NoneGridLocation
from grid.grid_service import GridService
from services.envelope_services_interface import EnvelopeServicesInterface


class Slide:
    def __init__(self, service: EnvelopeServicesInterface,
                 package_type: PackageType, drone_azimuth: Angle, drop_azimuth: Angle,
                 cell_resolution: int, cell_ratio_required: float):
        self._service = service
        self._package_type = package_type
        self._drone_azimuth = drone_azimuth
        self._drop_azimuth = drop_azimuth
        self._cell_resolution = cell_resolution
        self._cell_ratio_required = cell_ratio_required

        self._envelope_polygon = self._drop_envelope()
        self._envelope_centroid_location = GridService.get_polygon_centroid_cell(self._envelope_polygon, self._cell_resolution)
        self._envelope_boundary = PolygonUtils.get_envelope_boundary(self._envelope_locations)

    def __eq__(self, other):
        return (self.package_type == other.package_type) and \
               (self.drone_azimuth == other.drone_azimuth) and \
               (self.drop_azimuth == other.drop_azimuth) and \
               (self.cell_resolution == other.cell_resolution) and \
               (self.cell_ratio_required == other.cell_ratio_required)

    @property
    def service(self) -> EnvelopeServicesInterface:
        return self._service

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    @property
    def drone_azimuth(self) -> Angle:
        return self._drone_azimuth

    @property
    def drop_azimuth(self) -> Angle:
        return self._drop_azimuth

    @property
    def cell_resolution(self) -> int:
        return self._cell_resolution

    @property
    def cell_ratio_required(self) -> float:
        return self._cell_ratio_required

    @property
    def envelope_centroid_location(self) -> Union[GridLocation, NoneGridLocation]:
        return self._envelope_centroid_location

    def _drop_envelope(self) -> Union[Polygon2D, EmptyGeometry2D]:
        drop_point = create_point_2d(0, 0)
        return self._service.drop_envelope(self._package_type, self._drone_azimuth, drop_point, self._drop_azimuth)
