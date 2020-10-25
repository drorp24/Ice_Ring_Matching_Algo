from common.entities.package import PackageType
from common.math.angle import Angle
from geometry.geo_factory import create_polygon_2d, create_point_2d
from grid.cell import Location
from services.envelope_services_interface import EnvelopeServicesInterface


class Slide:
    def __init__(self, service: EnvelopeServicesInterface, package_type: PackageType, drone_azimuth: Angle,
                 drop_azimuth: Angle):
        self._service = service
        self._package_type = package_type
        self._drone_azimuth = drone_azimuth
        self._drop_azimuth = drop_azimuth

        self._envelope_locations = self._locate_envelope()

    def __eq__(self, other):
        return (self.drone_azimuth == other.drone_azimuth) and \
               (self.drop_azimuth == other.drop_azimuth) and \
               (self.package_type == other.package_type) and \
               (self.envelope_locations == other.envelope_locations)

    @property
    def service(self) -> Angle:
        return self._service

    @property
    def drone_azimuth(self) -> Angle:
        return self._drone_azimuth

    @property
    def drop_azimuth(self) -> Angle:
        return self._drop_azimuth

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    @property
    def envelope_locations(self) -> list[Location]:
        return self._envelope_locations

    def _locate_envelope(self) -> list[Location]:

        drop_point = create_point_2d(0, 0)
        polygon = self._service.drop_envelope(self._package_type, self._drone_azimuth, drop_point,self._drop_azimuth)

        # split polygon to boxes

        # get the indices of the polygon
        # check the area in each box
        pass
