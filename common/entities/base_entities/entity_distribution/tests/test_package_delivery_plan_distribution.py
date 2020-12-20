import unittest
from math import sqrt
from random import Random

from common.entities.base_entities.entity_distribution.package_delivery_plan_distribution import \
    PackageDeliveryPlanDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import create_point_2d


class BasicCustomerDeliveryDistribTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pitch_distrib = AngleUniformDistribution(start_angle=Angle(20, AngleUnit.DEGREE),
                                                 end_angle=Angle(60, AngleUnit.DEGREE))
        cls.loc_distrib = UniformPointInBboxDistribution(min_x=-10, max_x=10, min_y=-10, max_y=10)
        cls.pdp_distrib = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib,
                                                          relative_location_distribution=cls.loc_distrib)

        cls.base_point = create_point_2d(1000, 2000)
        cls.num_of_pdps_to_sample = 7
        cls.pdp_samples = cls.pdp_distrib.choose_rand(random=Random(),
                                                      base_loc=cls.base_point,
                                                      amount=cls.num_of_pdps_to_sample)

    def test_random_local_sample_is_within_range(self):
        max_dist = 10 * 2 / sqrt(2)
        within_valid_range = [pdp.calc_location().calc_distance_to_point(self.base_point) < max_dist
                              for pdp in self.pdp_samples]
        self.assertTrue(all(within_valid_range))

    def test_random_local_sample_amounts_are_correct(self):
        self.assertEqual(len(self.pdp_samples), self.num_of_pdps_to_sample)
