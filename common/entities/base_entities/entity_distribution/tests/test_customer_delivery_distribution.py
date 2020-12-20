import unittest

from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution
from common.entities.base_entities.entity_distribution.package_delivery_plan_distribution import \
    PackageDeliveryPlanDistribution
from common.math.angle import AngleUniformDistribution, Angle, AngleUnit
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION


class BasicCustomerDeliveryDistribTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pitch_distrib_1 = AngleUniformDistribution(start_angle=Angle(20, AngleUnit.DEGREE),
                                                   end_angle=Angle(60, AngleUnit.DEGREE))
        cls.location_distrib1 = UniformPointInBboxDistribution(min_x=10, max_x=10, min_y=11, max_y=11)
        cls.plan_delivery_distribution1 = PackageDeliveryPlanDistribution(pitch_distribution=pitch_distrib_1,
                                                                          relative_location_distribution=cls.location_distrib1)
        cls.loc_distrib = DEFAULT_ZERO_LOCATION_DISTRIBUTION
        cls.cd_dist = CustomerDeliveryDistribution(relative_location_distribution=cls.loc_distrib,
                                                   package_delivery_plan_distributions=[cls.plan_delivery_distribution1])

    def test_random_sample_from_distrib