import statistics
from math import cos, sin

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from geometry.geo2d import Polygon2D, Point2D
from geometry.geo_factory import create_point_2d, create_vector_2d, create_polygon_2d_from_ellipse
from services.envelope_services_interface import EnvelopeServicesInterface


class MockEnvelopeServices(EnvelopeServicesInterface):

    @classmethod
    def _calc_envelope(cls, package_type: PackageType, envelope_center: Point2D, drone_azimuth: Angle,
                       drop_azimuth: Angle) -> Polygon2D:
        if drone_azimuth.in_degrees() < 0 or drone_azimuth.in_degrees() > 360:
            raise ValueError("Azimuth should be between 0-360 degrees.")
        envelope_width = (package_type.value.potential_drop_envelope.maximal_radius_meters -
                          package_type.value.potential_drop_envelope.minimal_radius_meters)
        if abs(drop_azimuth.in_degrees() - drone_azimuth.in_degrees()) < 90:
            drop_and_drone_azimuth_dot = (create_vector_2d(cos(drop_azimuth.in_radians()),
                                                           sin(drop_azimuth.in_radians()))
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

    @classmethod
    def drop_envelope(cls, package_type: PackageType, drone_azimuth: Angle, drop_point: Point2D,
                      drop_azimuth: Angle) -> Polygon2D:
        drone_arrival_angle_in_rad = Angle(180 + drone_azimuth.in_degrees(), AngleUnit.DEGREE).in_radians()
        average_radius = statistics.mean([package_type.value.potential_drop_envelope.maximal_radius_meters,
                                          package_type.value.potential_drop_envelope.minimal_radius_meters])
        envelope_center = create_point_2d(drop_point.x +
                                          (average_radius * cos(drone_arrival_angle_in_rad)),
                                          drop_point.y +
                                          (average_radius * sin(drone_arrival_angle_in_rad)))
        return cls._calc_envelope(package_type, envelope_center, drone_azimuth, drop_azimuth)

    @classmethod
    def delivery_envelope(cls, package_type: PackageType, drone_location: Point2D, drone_azimuth: Angle,
                          drop_azimuth: Angle) -> Polygon2D:
        average_radius = statistics.mean([package_type.value.potential_drop_envelope.maximal_radius_meters,
                                          package_type.value.potential_drop_envelope.minimal_radius_meters])
        envelope_center = create_point_2d(drone_location.x +
                                          (average_radius * cos(drone_azimuth.in_radians())),
                                          drone_location.y +
                                          (average_radius * sin(drone_azimuth.in_radians())))
        return cls._calc_envelope(package_type, envelope_center, drone_azimuth, drop_azimuth)
