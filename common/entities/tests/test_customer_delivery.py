import unittest
from pprint import pprint
from random import Random

from common.entities.customer_delivery import CustomerDeliveryDistribution, CustomerDelivery
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import create_point_2d


class BasicCustomerDeliveryTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pitch_distrib_1 = AngleUniformDistribution(start_angle=Angle(20, AngleUnit.DEGREE),
                                                   end_angle=Angle(60, AngleUnit.DEGREE))
        pitch_distrib_2 = AngleUniformDistribution(start_angle=Angle(0, AngleUnit.DEGREE),
                                                   end_angle=Angle(50, AngleUnit.DEGREE))
        cls.location_distrib1 = UniformPointInBboxDistribution(min_x=10, max_x=10, min_y=11, max_y=11)
        cls.location_distrib2 = UniformPointInBboxDistribution(min_x=210, max_x=210, min_y=211, max_y=211)
        cls.plan_delivery_distribution1 = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib_1,
                                                                          drop_point_distribution=cls.location_distrib1)
        cls.plan_delivery_distribution2 = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib_2,
                                                                          drop_point_distribution=cls.location_distrib2)
        cls.cd_dist = CustomerDeliveryDistribution(
            [cls.plan_delivery_distribution1, cls.plan_delivery_distribution2])

    def test_calc_centroid(self):
        dist1 = [self.plan_delivery_distribution1]
        cd = CustomerDeliveryDistribution(dist1).choose_rand(Random(42), amount=1, num_pdp=10)[0]
        self.assertEqual(create_point_2d(10, 11), cd.calc_location())

        dist2 = [self.plan_delivery_distribution2]
        cd = CustomerDeliveryDistribution(dist2).choose_rand(Random(42), amount=1, num_pdp=10)[0]
        self.assertEqual(create_point_2d(210, 211), cd.calc_location())

    def print_example_customer_delivery(self):
        pprint(self.cd_dist.choose_rand(Random(100), 50)[0].__dict__())
