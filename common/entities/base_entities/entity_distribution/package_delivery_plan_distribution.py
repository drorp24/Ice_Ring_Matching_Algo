from __future__ import annotations

from random import Random
from typing import List
from uuid import UUID

from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import Distribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.distribution.geo_distribution import PointLocationDistribution, \
    DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

DEFAULT_RELATIVE_DROP_DISTRIB = DEFAULT_ZERO_LOCATION_DISTRIBUTION
DEFAULT_AZI_DISTRIB = AngleUniformDistribution(Angle(0, AngleUnit.DEGREE), Angle(355, AngleUnit.DEGREE))
DEFAULT_PITCH_DISTRIB = AngleUniformDistribution(Angle(30, AngleUnit.DEGREE), Angle(90, AngleUnit.DEGREE))
DEFAULT_PACKAGE_DISTRIB = PackageDistribution()


class PackageDeliveryPlanDistribution(Distribution):

    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 azimuth_distribution: AngleUniformDistribution = DEFAULT_AZI_DISTRIB,
                 pitch_distribution: AngleUniformDistribution = DEFAULT_PITCH_DISTRIB,
                 package_type_distribution: PackageDistribution = DEFAULT_PACKAGE_DISTRIB):
        self._relative_drop_point_distribution = relative_location_distribution
        self._azimuth_distribution = azimuth_distribution
        self._pitch_distribution = pitch_distribution
        self._package_type_distribution = package_type_distribution

    def choose_rand(self, random: Random,
                    base_loc: Point2D = create_point_2d(0, 0), amount: int = 1) -> List[PackageDeliveryPlan]:
        relative_drop_points = self._relative_drop_point_distribution.choose_rand(random=random, amount=amount)
        azimuths = self._azimuth_distribution.choose_rand(random=random, amount=amount)
        pitches = self._pitch_distribution.choose_rand(random=random, amount=amount)
        packages = self._package_type_distribution.choose_rand(random=random, amount=amount)
        uuid_seed = random.getrandbits(128)
        return [
            PackageDeliveryPlan(UUID(int=uuid_seed), drop_point=d_p + base_loc, azimuth=az, pitch=ptc, package_type=p_t)
            for (d_p, az, ptc, p_t) in zip(relative_drop_points, azimuths, pitches, packages)]
