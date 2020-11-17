from typing import Union

from common.entities.package import PackageType
from common.math.angle import Angle
from geometry.geo2d import Polygon2D, Point2D, EmptyGeometry2D
from geometry.geo_factory import create_polygon_2d_from_ellipse
from services.envelope_services_interface import EnvelopeServicesInterface


class MockEnvelopeServices(EnvelopeServicesInterface):

    @classmethod
    def _calc_envelope(cls, package_type: PackageType, envelope_center: Point2D, drone_azimuth: Angle,
                       drop_azimuth: Angle) -> Union[Polygon2D, EmptyGeometry2D]:
        envelope_width = package_type.value.calc_potential_drop_envelope().calc_delta_between_radii()
        envelope_height = envelope_width * drop_azimuth.to_direction().dot(drone_azimuth.to_direction())
        if drop_azimuth.calc_abs_difference(drone_azimuth).degrees >= 90:
            envelope_height = 0
        return create_polygon_2d_from_ellipse(ellipse_center=envelope_center,
                                              ellipse_width=envelope_width,
                                              ellipse_height=envelope_height,
                                              ellipse_rotation_deg=drone_azimuth.degrees)

    @classmethod
    def calc_drop_envelope(cls, package_type: PackageType, drone_azimuth: Angle, drop_point: Point2D,
                      drop_azimuth: Angle) -> Union[Polygon2D, EmptyGeometry2D]:
        average_radius = package_type.value.calc_potential_drop_envelope().average_radius_meters
        envelope_center = drop_point.add_vector(drone_azimuth.calc_reverse().to_direction() * average_radius)
        return cls._calc_envelope(package_type, envelope_center, drone_azimuth, drop_azimuth)

    @classmethod
    def calc_delivery_envelope(cls, package_type: PackageType, drone_location: Point2D, drone_azimuth: Angle,
                          drop_azimuth: Angle) -> Union[Polygon2D, EmptyGeometry2D]:
        average_radius = package_type.value.calc_potential_drop_envelope().average_radius_meters
        envelope_center = drone_location.add_vector(drone_azimuth.to_direction() * average_radius)
        return cls._calc_envelope(package_type, envelope_center, drone_azimuth, drop_azimuth)

    @staticmethod
    def is_valid_envelope(polygon: Polygon2D, required_area: float) -> bool:
        if polygon.calc_area() < required_area:
            return False

        return True

