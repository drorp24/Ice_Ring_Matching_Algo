from __future__ import annotations

from random import Random
from typing import List

from common.entities.disribution.distribution import Distribution
from common.entities.base_entity import JsonableBaseEntity, Localizable
from common.entities.package import PackageType, PackageDistribution
from common.math.angle import Angle, AngleUniformDistribution, AngleUnit
from geometry.geo2d import Point2D, Polygon2D
from geometry.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import create_polygon_2d_from_ellipse, convert_dict_to_point_2d


class PackageDeliveryPlan(JsonableBaseEntity, Localizable):

    def __init__(self, drop_point: Point2D, azimuth: Angle, pitch: Angle, package_type: PackageType):
        self._drop_point = drop_point
        self._azimuth = azimuth
        self._pitch = pitch
        self._package_type = package_type

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    @property
    def azimuth(self) -> Angle:
        return self._azimuth

    @property
    def pitch(self) -> Angle:
        return self._pitch

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    def calc_location(self) -> Point2D:
        return self.drop_point

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return PackageDeliveryPlan(drop_point=convert_dict_to_point_2d(dict_input['drop_point']),
                                   azimuth=Angle.dict_to_obj(dict_input['azimuth']),
                                   pitch=Angle.dict_to_obj(dict_input['pitch']),
                                   package_type=PackageType.dict_to_obj(dict_input['package_type']))

    def calc_drop_envelope(self, drone_azimuth: Angle) -> Polygon2D:
        average_radius = self.package_type.value.calc_potential_drop_envelope().average_radius_meters
        envelope_center = self._drop_point.add_vector(drone_azimuth.calc_reverse().to_direction() * average_radius)
        return self._calc_envelope(envelope_center, drone_azimuth)

    def calc_delivery_envelope(self, drone_location: Point2D, drone_azimuth: Angle) -> Polygon2D:
        average_radius = self.package_type.value.calc_potential_drop_envelope().average_radius_meters
        envelope_center = drone_location.add_vector(drone_azimuth.to_direction() * average_radius)
        return self._calc_envelope(envelope_center, drone_azimuth)

    def _calc_envelope(self, envelope_center: Point2D, drone_azimuth: Angle) -> Polygon2D:
        envelope_width = self.package_type.value.calc_potential_drop_envelope().calc_delta_between_radii()
        envelope_height = envelope_width * self._azimuth.to_direction().dot(drone_azimuth.to_direction())
        if self._azimuth.calc_abs_difference(drone_azimuth).degrees >= 90:
            envelope_height = 0
        return create_polygon_2d_from_ellipse(ellipse_center=envelope_center,
                                              ellipse_width=envelope_width,
                                              ellipse_height=envelope_height,
                                              ellipse_rotation_deg=drone_azimuth.degrees)

    def __hash__(self):
        return hash((self.drop_point, self.azimuth, self.pitch, self.package_type))

    def __str__(self):
        return 'Package Delivery Plan: ' + str((self.drop_point, self.azimuth, self.pitch, self.package_type))

    def __eq__(self, other):
        return (self.drop_point == other.drop_point) and \
               (self.azimuth == other.azimuth) and \
               (self.pitch == other.pitch) and \
               (self.package_type == other.package_type)


DEFAULT_DROP_POINT_DISTRIB = UniformPointInBboxDistribution(30, 40, 35, 45)
DEFAULT_AZI_DISTRIB = AngleUniformDistribution(Angle(0, AngleUnit.DEGREE), Angle(355, AngleUnit.DEGREE))
DEFAULT_PITCH_DISTRIB = AngleUniformDistribution(Angle(30, AngleUnit.DEGREE), Angle(90, AngleUnit.DEGREE))
DEFAULT_PACKAGE_DISTRIB = PackageDistribution()


class PackageDeliveryPlanDistribution(Distribution):

    def __init__(self,
                 drop_point_distribution: UniformPointInBboxDistribution = DEFAULT_DROP_POINT_DISTRIB,
                 azimuth_distribution: AngleUniformDistribution = DEFAULT_AZI_DISTRIB,
                 pitch_distribution: AngleUniformDistribution = DEFAULT_PITCH_DISTRIB,
                 package_type_distribution: PackageDistribution = DEFAULT_PACKAGE_DISTRIB):
        self._drop_point_distribution = drop_point_distribution
        self._azimuth_distribution = azimuth_distribution
        self._pitch_distribution = pitch_distribution
        self._package_type_distribution = package_type_distribution

    def choose_rand(self, random: Random, amount: int = 1) -> List[PackageDeliveryPlan]:
        drop_points = self._drop_point_distribution.choose_rand(random, amount)
        azimuths = self._azimuth_distribution.choose_rand(random, amount)
        pitchs = self._pitch_distribution.choose_rand(random, amount)
        packages = self._package_type_distribution.choose_rand(random, amount)
        return [PackageDeliveryPlan(dp, az, el, pk) for (dp, az, el, pk) in
                zip(drop_points, azimuths, pitchs, packages)]
