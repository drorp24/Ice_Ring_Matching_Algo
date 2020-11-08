import unittest
from pprint import pprint
from random import Random

from common.entities.customer_delivery import CustomerDeliveryDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit


class BasicPackageDeliveryPlan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pitch_distrib_1 = AngleUniformDistribution(start_angle=Angle(20, AngleUnit.DEGREE),
                                                       end_angle=Angle(60, AngleUnit.DEGREE))
        pitch_distrib_2 = AngleUniformDistribution(start_angle=Angle(0, AngleUnit.DEGREE),
                                                       end_angle=Angle(50, AngleUnit.DEGREE))
        cls.plan_delivery_distribution1 = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib_1)
        cls.plan_delivery_distribution2 = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib_2)
        cls.cd_dist = CustomerDeliveryDistribution(
            [cls.plan_delivery_distribution1, cls.plan_delivery_distribution2])

    def test_generate_package_delivery_plans_based_on_distribution(self):
        print(self.cd_dist.choose_rand(random=Random(), amount=20))

    def test_to_dict(self):
        pprint(dict(self.cd_dist.choose_rand(Random(100), 50)[0].__dict__()))
