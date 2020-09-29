from common.entities.package import Package, PackageType
from geometry.geo2d import Point2D, Vector2D, LinearRing2D, Polygon2D
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d, create_vector_2d, create_polygon_2d_from_ellipsis

import statistics
from math import cos, sin


class DropPoint:

    def __init__(self, point: Point2D):
        self._coordinates = point

    def __str__(self):
        return "({},{})".format(self._coordinates.x, self._coordinates.y)

    @property
    def coordinates(self):
        return self._coordinates


class PackageDeliveryPlan:

    def __init__(self, point: Point2D, azimuth: Angle, elevation: Angle, package_type: PackageType):
        self._drop_point = DropPoint(point)
        self._azimuth = azimuth
        self._elevation = elevation
        self._package = Package(package_type)

    @property
    def drop_point(self) -> DropPoint:
        return self._drop_point

    @property
    def azimuth(self) -> Angle:
        return self._azimuth

    @property
    def elevation(self) -> Angle:
        return self._elevation

    @property
    def package(self) -> Package:
        return self._package

    def drop_envelope(self, drone_azimuth: Angle) -> Polygon2D:
        drone_arrival_angle_in_rad = Angle(180 + drone_azimuth.in_degrees(), AngleUnit.DEGREE).in_radians()
        average_radius = statistics.mean([self._package.potential_drop_envelope.maximal_radius_meters,
                                          self.package.potential_drop_envelope.minimal_radius_meters])
        envelope_center = create_point_2d(self._drop_point.coordinates.x + (average_radius * cos(drone_arrival_angle_in_rad)),
                                          self.drop_point.coordinates.y + (average_radius * sin(drone_arrival_angle_in_rad)))
        envelope_width = self._package.potential_drop_envelope.maximal_radius_meters - self.package.potential_drop_envelope.minimal_radius_meters
        envelope_height = envelope_width * create_vector_2d(cos(self.azimuth.in_radians()), sin(self.azimuth.in_radians())).dot(
            create_vector_2d(cos(drone_arrival_angle_in_rad), sin(drone_arrival_angle_in_rad))
        )
        return create_polygon_2d_from_ellipsis(ellipsis_center=(envelope_center.x, envelope_center.y),
                                               ellipsis_width=envelope_width,
                                               ellipsis_height=envelope_height,
                                               ellipsis_rotation=drone_azimuth.in_degrees())