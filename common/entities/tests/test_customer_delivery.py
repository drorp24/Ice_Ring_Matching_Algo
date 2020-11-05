import unittest
from random import Random

from common.entities.customer_delivery import CustomerDeliveryDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit


class BasicPackageDeliveryPlan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        elevation_distrib_1 = AngleUniformDistribution(start_angle=Angle(20, AngleUnit.DEGREE),
                                                       end_angle=Angle(60, AngleUnit.DEGREE))
        elevation_distrib_2 = AngleUniformDistribution(start_angle=Angle(0, AngleUnit.DEGREE),
                                                       end_angle=Angle(50, AngleUnit.DEGREE))
        cls.plan_delivery_distribution1 = PackageDeliveryPlanDistribution(elevation_distribution=elevation_distrib_1)
        cls.plan_delivery_distribution2 = PackageDeliveryPlanDistribution(elevation_distribution=elevation_distrib_2)
        cls.package_delivery_distrib = CustomerDeliveryDistribution(
            [cls.plan_delivery_distribution1, cls.plan_delivery_distribution2])
    
    def test_generate_package_delivery_plans_based_on_distribution(self):
        print(self.package_delivery_distrib.choose_rand(random=Random(), num_to_choose=20))

