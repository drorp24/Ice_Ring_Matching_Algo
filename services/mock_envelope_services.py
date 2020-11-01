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
        envelope_width = package_type.value.potential_drop_envelope.calc_delta_between_radii()
        envelope_height = envelope_width * drop_azimuth.to_direction().dot(drone_azimuth.to_direction())
        if drop_azimuth.calc_abs_difference(drone_azimuth).in_degrees() >= 90:
            envelope_height = 0
        return create_polygon_2d_from_ellipse(ellipse_center=envelope_center,
                                              ellipse_width=envelope_width,
                                              ellipse_height=envelope_height,
                                              ellipse_rotation_deg=drone_azimuth.in_degrees())

    @classmethod
    def drop_envelope(cls, package_type: PackageType, drone_azimuth: Angle, drop_point: Point2D,
                      drop_azimuth: Angle) -> Polygon2D:
        average_radius = package_type.value.potential_drop_envelope.average_radius_meters
        envelope_center = drop_point.add_vector(drone_azimuth.calc_reverse().to_direction() * average_radius)
        return cls._calc_envelope(package_type, envelope_center, drone_azimuth, drop_azimuth)


    @classmethod
    def delivery_envelope(cls, package_type: PackageType, drone_location: Point2D, drone_azimuth: Angle,
                          drop_azimuth: Angle) -> Polygon2D:
        average_radius = package_type.value.potential_drop_envelope.average_radius_meters
        envelope_center = drone_location.add_vector(drone_azimuth.to_direction() * average_radius)
        return cls._calc_envelope(package_type, envelope_center, drone_azimuth, drop_azimuth)

