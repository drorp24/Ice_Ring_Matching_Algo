import unittest
from math import sqrt
from random import Random

from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution
from common.entities.base_entities.entity_distribution.package_delivery_plan_distribution import \
    PackageDeliveryPlanDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo_factory import create_point_2d


class BasicCustomerDeliveryDistribTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pitch_distrib_1 = AngleUniformDistribution(start_angle=Angle(20, AngleUnit.DEGREE),
                                                   end_angle=Angle(60, AngleUnit.DEGREE))
        cls.location_distrib1 = UniformPointInBboxDistribution(min_x=-10, max_x=10, min_y=-10, max_y=10)
        cls.plan_delivery_distribution1 = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib_1,
                                                                          relative_location_distribution=cls.location_distrib1)
        cls.loc_distrib = DEFAULT_ZERO_LOCATION_DISTRIBUTION
        cls.cd_dist = CustomerDeliveryDistribution(relative_location_distribution=cls.loc_distrib,
                                                   package_delivery_plan_distributions=[
                                                       cls.plan_delivery_distribution1])

    def test_random_local_sample_is_within_range(self):
        center_point = create_point_2d(1000, 2000)
        cds = self.cd_dist.choose_rand(random=Random(), base_loc=center_point, amount=10, num_pdp=7)
        within_valid_range_from_center = [cd.calc_location().calc_distance_to_point(center_point) < 10 * sqrt(2) / 2 for cd in cds]
        self.assertTrue(all(within_valid_range_from_center))

    def test_random_local_sample_amounts_are_correct(self):
        center_point = create_point_2d(1000, 2000)
        num_of_cds = 10
        num_of_pdps = 7
        cds = self.cd_dist.choose_rand(random=Random(), base_loc=center_point, amount=num_of_cds, num_pdp=num_of_pdps)
        self.assertEqual(len(cds), num_of_cds)
        self.assertTrue(all([len(cd.package_delivery_plans) is num_of_pdps for cd in cds]))
