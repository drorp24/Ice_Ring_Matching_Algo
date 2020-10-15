from common.entities.package import PackageType
from geometry.geo2d import Point2D, Polygon2D
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d, create_vector_2d, create_polygon_2d_from_ellipse

import statistics
from math import cos, sin


class PackageDeliveryPlan:

    def __init__(self, drop_point: Point2D, azimuth: Angle, elevation: Angle, package_type: PackageType):
        self._drop_point = drop_point
        self._azimuth = azimuth
        self._elevation = elevation
        self._package_type = package_type

    def __eq__(self, other):
        return (self.drop_point == other.drop_point) and \
               (self.azimuth == other.azimuth) and \
               (self.elevation == other.elevation) and \
               (self.package_type == other.package_type)

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    @property
    def azimuth(self) -> Angle:
        return self._azimuth

    @property
    def elevation(self) -> Angle:
        return self._elevation

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    def _calc_envelope(self, envelope_center: Point2D, drone_azimuth: Angle) -> Polygon2D:
        if drone_azimuth.in_degrees() < 0 or drone_azimuth.in_degrees() > 360:
            raise ValueError("Azimuth should be between 0-360 degrees.")
        envelope_width = (self.package_type.value.potential_drop_envelope.maximal_radius_meters -
                          self.package_type.value.potential_drop_envelope.minimal_radius_meters)
        if abs(self._azimuth.in_degrees() - drone_azimuth.in_degrees()) < 90:
            drop_and_drone_azimuth_dot = (create_vector_2d(cos(self._azimuth.in_radians()),
                                                           sin(self._azimuth.in_radians()))
                                          .dot(
                                        create_vector_2d(cos(drone_azimuth.in_radians()),
                                                         sin(drone_azimuth.in_radians()))))
            envelope_height = envelope_width * drop_and_drone_azimuth_dot
        else:
            envelope_height = 0
        return create_polygon_2d_from_ellipse(ellipse_center=(envelope_center.x, envelope_center.y),
                                              ellipse_width=envelope_width,
                                              ellipse_height=envelope_height,
                                              ellipse_rotation=drone_azimuth.in_degrees())

    def drop_envelope(self, drone_azimuth: Angle) -> Polygon2D:
        drone_arrival_angle_in_rad = Angle(180 + drone_azimuth.in_degrees(), AngleUnit.DEGREE).in_radians()
        average_radius = statistics.mean([self.package_type.value.potential_drop_envelope.maximal_radius_meters,
                                          self.package_type.value.potential_drop_envelope.minimal_radius_meters])
        envelope_center = create_point_2d(self._drop_point.x +
                                          (average_radius * cos(drone_arrival_angle_in_rad)),
                                          self._drop_point.y +
                                          (average_radius * sin(drone_arrival_angle_in_rad)))
        return self._calc_envelope(envelope_center, drone_azimuth)

    def delivery_envelope(self, drone_location: Point2D, drone_azimuth: Angle) -> Polygon2D:
        average_radius = statistics.mean([self.package_type.value.potential_drop_envelope.maximal_radius_meters,
                                          self.package_type.value.potential_drop_envelope.minimal_radius_meters])
        envelope_center = create_point_2d(drone_location.x +
                                          (average_radius * cos(drone_azimuth.in_radians())),
                                          drone_location.y +
                                          (average_radius * sin(drone_azimuth.in_radians())))
        return self._calc_envelope(envelope_center, drone_azimuth)
