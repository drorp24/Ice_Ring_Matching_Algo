from optional import Optional

from common.entities.package import PackageType
from common.math.angle import Angle
from geometry.geo_factory import create_point_2d
from grid.grid_location import GridLocation
from grid.grid_service import GridService
from services.envelope_services_interface import EnvelopeServicesInterface


class Slide:
    def __init__(self, envelope_service: EnvelopeServicesInterface,
                 package_type: PackageType, drone_azimuth: Angle, drop_azimuth: Angle,
                 cell_width_resolution: float, cell_height_resolution: float, required_area: float):
        self._envelope_service = envelope_service
        self._package_type = package_type
        self._drone_azimuth = drone_azimuth
        self._drop_azimuth = drop_azimuth
        self._cell_width_resolution = cell_width_resolution
        self._cell_height_resolution = cell_height_resolution
        self._required_area = required_area

        self._envelope_location = self.calc_envelope_location()

    def __eq__(self, other):
        return (self.package_type == other.package_type) and \
               (self.drone_azimuth == other.drone_azimuth) and \
               (self.drop_azimuth == other.drop_azimuth) and \
               (self.cell_width_resolution == other.cell_width_resolution) and \
               (self.cell_height_resolution == other.cell_height_resolution) and \
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
    def cell_width_resolution(self) -> float:
        return self._cell_width_resolution

    @property
    def cell_height_resolution(self) -> float:
        return self._cell_height_resolution

    @property
    def required_area(self) -> float:
        return self._required_area

    @property
    def envelope_location(self) -> Optional.of(GridLocation):
        return self._envelope_location

    def calc_envelope_location(self) -> Optional.of(GridLocation):
        drop_point = create_point_2d(0, 0)
        envelope_polygon = self._envelope_service.calc_drop_envelope(self._package_type, self._drone_azimuth,
                                                                     drop_point,
                                                                     self._drop_azimuth)

        if not self._envelope_service.is_valid_envelope(envelope_polygon, self._required_area):
            return Optional.empty()

        return Optional.of(GridService.get_polygon_centroid_grid_location(envelope_polygon, self._cell_width_resolution,
                                                                          self._cell_height_resolution))

    def __repr__(self):
        return "Slide ({0} {1} {2} {3})".format(self.package_type,
                                                self.drone_azimuth.degrees,
                                                self.drop_azimuth.degrees,
                                                self.envelope_location if self.envelope_location.is_empty()
                                                else
                                                "{0}:{1}".format(self.envelope_location.get().column,
                                                                 self.envelope_location.get().row))
