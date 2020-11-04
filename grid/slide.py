from typing import Union

from common.entities.package import PackageType
from common.math.angle import Angle
from geometry.geo2d import EmptyGeometry2D
from geometry.geo_factory import create_point_2d
from grid.cell import GridLocation, NoneGridLocation
from grid.grid_service import GridService
from services.envelope_services_interface import EnvelopeServicesInterface


class Slide:
    def __init__(self, envelope_service: EnvelopeServicesInterface,
                 package_type: PackageType, drone_azimuth: Angle, drop_azimuth: Angle,
                 cell_resolution: int, required_area: float):
        self._envelope_service = envelope_service
        self._package_type = package_type
        self._drone_azimuth = drone_azimuth
        self._drop_azimuth = drop_azimuth
        self._cell_resolution = cell_resolution
        self._required_area = required_area

        self._envelope_location = self.calc_envelope_location()
        # self._envelope_boundary = PolygonUtils.get_envelope_boundary(self._envelope_locations)

    def __eq__(self, other):
        return (self.package_type == other.package_type) and \
               (self.drone_azimuth == other.drone_azimuth) and \
               (self.drop_azimuth == other.drop_azimuth) and \
               (self.cell_resolution == other.cell_resolution) and \
               (self.required_area == other.required_area)

    @property
    def envelope_service(self) -> EnvelopeServicesInterface:
        return self._envelope_service

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
    def required_area(self) -> float:
        return self._required_area

    @property
    def envelope_location(self) -> GridLocation:
        return self._envelope_location

    def calc_envelope_location(self) -> GridLocation:

        drop_point = create_point_2d(0, 0)
        envelope_polygon = self._envelope_service.drop_envelope(self._package_type, self._drone_azimuth, drop_point,
                                                                self._drop_azimuth)

        if not self._envelope_service.is_valid_envelope(envelope_polygon, self._required_area):
            return NoneGridLocation()

        return GridService.get_polygon_centroid_grid_location(envelope_polygon, self._cell_resolution)
