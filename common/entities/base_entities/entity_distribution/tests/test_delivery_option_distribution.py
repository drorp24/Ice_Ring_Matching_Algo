import unittest
from math import sqrt
from random import Random

from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution
from common.entities.base_entities.entity_distribution.package_delivery_plan_distribution import \
    PackageDeliveryPlanDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo_factory import create_point_2d


class BasicDeliveryOptionDistribTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pitch_distrib = AngleUniformDistribution(start_angle=Angle(20, AngleUnit.DEGREE),
                                                 end_angle=Angle(60, AngleUnit.DEGREE))
        cls.pdp_loc_distrib = UniformPointInBboxDistribution(min_x=-10, max_x=10, min_y=-10, max_y=10)
        cls.plan_delivery_distribution1 = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib,
                                                                          relative_location_distribution=cls.pdp_loc_distrib)
        cls.cd_loc_distrib = DEFAULT_ZERO_LOCATION_DISTRIBUTION
        cls.cd_dist = CustomerDeliveryDistribution(relative_location_distribution=cls.cd_loc_distrib,
                                                   package_delivery_plan_distributions=[
                                                       cls.plan_delivery_distribution1])

        cls.do_dist = DeliveryOptionDistribution(relative_location_distribution=
                                                 UniformPointInBboxDistribution(min_x=-10, max_x=10, min_y=-10,
                                                                                max_y=10),
                                                 customer_delivery_distributions=[cls.cd_dist])
        cls.base_point = create_point_2d(1000, 2000)
        cls.num_of_dos_to_sample = 10
        cls.num_of_cds_to_sample = 7
        cls.num_of_pdps_to_sample = 3
        cls.do_samples = cls.do_dist.choose_rand(random=Random(),
                                                 base_loc=cls.base_point,
                                                 amount=cls.num_of_dos_to_sample,
                                                 num_cd=cls.num_of_cds_to_sample,
                                                 num_pdp=cls.num_of_pdps_to_sample)

    def test_random_local_sample_is_within_range(self):
        max_dist = 10 * 2 * 2 / sqrt(2)
        within_valid_range = [do.calc_location().calc_distance_to_point(self.base_point) < max_dist
                              for do in self.do_samples]
        self.assertTrue(all(within_valid_range))

    def test_random_local_sample_amounts_are_correct(self):
        self.assertEqual(len(self.do_samples), self.num_of_dos_to_sample)
        self.assertTrue(all([len(do.customer_deliveries) is self.num_of_cds_to_sample
                             for do in self.do_samples]))
        self.assertTrue(all([[len(cd.package_delivery_plans) is self.num_of_pdps_to_sample
                              for cd in do.customer_deliveries] for do in self.do_samples]))
