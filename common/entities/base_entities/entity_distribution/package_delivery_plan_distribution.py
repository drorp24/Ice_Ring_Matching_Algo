from __future__ import annotations

import math
from random import Random
from typing import List, Dict, Union

from common.entities.base_entities.entity_distribution.distribution_utils import LocalDistribution
from common.entities.base_entities.entity_distribution.entity_id_distribution import EntityIDDistribution, \
    DEFAULT_SINGLE_ID_DISTRIB
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import Distribution, Range, UniformDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.distribution.geo_distribution import PointLocationDistribution, \
    DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo2d import Point2D
from geometry.geo_factory import create_zero_point_2d

DEFAULT_RELATIVE_DROP_DISTRIB = DEFAULT_ZERO_LOCATION_DISTRIBUTION
DEFAULT_AZI_DISTRIB = AngleUniformDistribution(Angle(0, AngleUnit.DEGREE), Angle(355, AngleUnit.DEGREE))
DEFAULT_PITCH_DISTRIB = AngleUniformDistribution(Angle(30, AngleUnit.DEGREE), Angle(90, AngleUnit.DEGREE))
DEFAULT_PACKAGE_DISTRIB = PackageDistribution()


class PackageDeliveryPlanDistribution(Distribution):

    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 id_distribution: EntityIDDistribution = DEFAULT_SINGLE_ID_DISTRIB,
                 azimuth_distribution: AngleUniformDistribution = DEFAULT_AZI_DISTRIB,
                 pitch_distribution: AngleUniformDistribution = DEFAULT_PITCH_DISTRIB,
                 package_type_distribution: PackageDistribution = DEFAULT_PACKAGE_DISTRIB):
        self._relative_drop_point_distribution = relative_location_distribution
        self._id_distribution = id_distribution
        self._azimuth_distribution = azimuth_distribution
        self._pitch_distribution = pitch_distribution
        self._package_type_distribution = package_type_distribution

    def choose_rand(self, random: Random, base_loc: Point2D = create_zero_point_2d(), amount: Union[int, Range] = 1) -> List[
        PackageDeliveryPlan]:
        if isinstance(amount, Range):
            amount = math.floor(UniformDistribution(amount).choose_uniform_in_range(random))
        sampled_distributions = self._calc_samples_from_distributions(amount, random)
        PackageDeliveryPlanDistribution._update_the_location_of_sampled_points(base_loc, sampled_distributions)
        pdp_attrib_samples = LocalDistribution.convert_list_dict_to_individual_dicts(sampled_distributions)
        return PackageDeliveryPlanDistribution._calc_result_list(pdp_attrib_samples)

    def _calc_samples_from_distributions(self, amount, random):
        return LocalDistribution.choose_rand_by_attrib(
            internal_sample_dict=
            {'id': self._id_distribution,
             'drop_point': self._relative_drop_point_distribution,
             'azimuth': self._azimuth_distribution,
             'pitch': self._pitch_distribution,
             'package_type': self._package_type_distribution
             }, random=random, amount=amount)

    @staticmethod
    def _update_the_location_of_sampled_points(base_loc: Point2D, sampled_distributions: Dict[str, list]):
        sampled_distributions['drop_point'] = LocalDistribution.add_base_point_to_relative_points(
            relative_points=sampled_distributions['drop_point'], base_point=base_loc)

    @staticmethod
    def _calc_result_list(pdp_attrib_samples: List[Dict]) -> List[PackageDeliveryPlan]:
        return [LocalDistribution.initialize_internal(PackageDeliveryPlan, pdp_dict) for pdp_dict in pdp_attrib_samples]
