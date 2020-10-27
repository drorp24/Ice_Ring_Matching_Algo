import math
from typing import List

from common.entities.package import PackageType
from common.math.angle import Angle
from geometry.geo_factory import create_point_2d
from geometry.utils import PolygonUtils
from grid.cell import Location
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

        self._envelope_locations = self._locate_envelope()

    def __eq__(self, other):
        return (self.drone_azimuth == other.drone_azimuth) and \
               (self.drop_azimuth == other.drop_azimuth) and \
               (self.package_type == other.package_type) and \
               (self.envelope_locations == other.envelope_locations)

    @property
    def service(self) -> EnvelopeServicesInterface:
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
    def envelope_locations(self) -> List[Location]:
        return self._envelope_locations

    def _locate_envelope(self) -> List[Location]:
        drop_point = create_point_2d(0, 0)
        polygon = self._service.drop_envelope(self._package_type, self._drone_azimuth, drop_point, self._drop_azimuth)

        required_area = PolygonUtils.convert_ratio_to_required_area(self._cell_resolution, self._cell_ratio_required)
        splitter_polygons = PolygonUtils.split_polygon(polygon, box_resolution=self._cell_resolution,
                                                       required_area=required_area)

        locations = []
        for split_polygon in splitter_polygons:
            bbox = split_polygon.bbox
            min_x, min_y = bbox.min_x, bbox.min_y
            min_x, min_y = math.floor(min_x / self._cell_resolution), math.floor(min_y / self._cell_resolution)

            locations.append(Location(min_x, min_y))

        return locations
