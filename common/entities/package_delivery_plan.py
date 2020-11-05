from __future__ import annotations

import itertools
from random import Random
from typing import Union, List

from common.entities.base_entities.distribution import UniformChoiceDistribution
from common.entities.package import PackageType, PackageDistribution
from common.math.angle import Angle, AngleUniformDistribution, AngleUnit
from geometry.geo2d import Point2D, Polygon2D
from geometry.geo_distribution import PointDistribution
from geometry.geo_factory import create_polygon_2d_from_ellipse


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

    def drop_envelope(self, drone_azimuth: Angle) -> Polygon2D:
        average_radius = self.package_type.value.potential_drop_envelope.average_radius_meters
        envelope_center = self._drop_point.add_vector(drone_azimuth.calc_reverse().to_direction() * average_radius)
        return self._calc_envelope(envelope_center, drone_azimuth)

    def delivery_envelope(self, drone_location: Point2D, drone_azimuth: Angle) -> Polygon2D:
        average_radius = self.package_type.value.potential_drop_envelope.average_radius_meters
        envelope_center = drone_location.add_vector(drone_azimuth.to_direction() * average_radius)
        return self._calc_envelope(envelope_center, drone_azimuth)

    def _calc_envelope(self, envelope_center: Point2D, drone_azimuth: Angle) -> Polygon2D:
        envelope_width = self.package_type.value.potential_drop_envelope.calc_delta_between_radii()
        envelope_height = envelope_width * self._azimuth.to_direction().dot(drone_azimuth.to_direction())
        if self._azimuth.calc_abs_difference(drone_azimuth).in_degrees() >= 90:
            envelope_height = 0
        return create_polygon_2d_from_ellipse(ellipse_center=envelope_center,
                                              ellipse_width=envelope_width,
                                              ellipse_height=envelope_height,
                                              ellipse_rotation_deg=drone_azimuth.in_degrees())

    def __hash__(self):
        return hash((self.drop_point, self.azimuth, self.elevation, self.package_type))

    def __str__(self):
        return 'Package Delivery Plan: ' + str((self.drop_point, self.azimuth, self.elevation, self.package_type))


_DEFAULT_DROP_POINT_DISTRIB = PointDistribution(30, 40, 35, 45)

_DEFAULT_AZI_DISTRIB = AngleUniformDistribution(Angle(0, AngleUnit.DEGREE), Angle(355, AngleUnit.DEGREE))

_DEFAULT_ELEVATION_DISTRIB = AngleUniformDistribution(Angle(30, AngleUnit.DEGREE), Angle(90, AngleUnit.DEGREE))

_DEFAULT_PACKAGE_DISTRIB = PackageDistribution()


class PackageDeliveryPlanDistribution:

    def __init__(self,
                 drop_point_distribution: PointDistribution = _DEFAULT_DROP_POINT_DISTRIB,
                 azimuth_distribution: AngleUniformDistribution = _DEFAULT_AZI_DISTRIB,
                 elevation_distribution: UniformChoiceDistribution = _DEFAULT_ELEVATION_DISTRIB,
                 package_type_distribution: PackageDistribution = _DEFAULT_PACKAGE_DISTRIB):
        self._drop_point_distribution = drop_point_distribution
        self._azimuth_distribution = azimuth_distribution
        self._elevation_distribution = elevation_distribution
        self._package_type_distribution = package_type_distribution

    def choose_rand(self, random: Random, num_to_choose: int = 1) -> List[PackageDeliveryPlan]:
        drop_points = self._drop_point_distribution.choose_rand(random, num_to_choose)
        azimuths = self._azimuth_distribution.choose_rand(random, num_to_choose)
        elevations = self._elevation_distribution.choose_rand(random, num_to_choose)
        packages = self._package_type_distribution.choose_rand(random, num_to_choose)
        return [PackageDeliveryPlan(dp, az, el, pk) for (dp, az, el, pk) in
                zip(drop_points, azimuths, elevations, packages)]
