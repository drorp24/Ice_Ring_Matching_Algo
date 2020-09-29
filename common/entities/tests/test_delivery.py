import unittest
from datetime import datetime

from time_window import TimeWindow

from common.entities.delivery_factory import create_customer_delivery, create_delivery_request, create_delivery_option
from common.entities.package import PackageType
from common.math.angle import create_radian_angle, create_degree_angle
from geometry.geo_factory import create_point_2d


class BasicDeliveryGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        point = create_point_2d(1, 2)

        cls.cd = create_customer_delivery(point, azimuth=create_degree_angle(30), elevation=create_degree_angle(80),
                                          package=PackageType.TINY)
        cls.do = create_delivery_option(point, azimuth=create_degree_angle(30), elevation=create_degree_angle(80),
                                        package=PackageType.TINY)

        cls.time_window = TimeWindow(datetime(2020, 1, 23, 11, 30, 00),
                                     datetime(2020, 1, 23, 11, 35, 00))
        cls.dr = create_delivery_request(point, azimuth=create_degree_angle(30), elevation=create_degree_angle(80),
                                         package=PackageType.TINY,
                                         time_window=cls.time_window, priority=10)

    def test_customer_delivery(self):
        self.assertEqual(self.cd.package_delivery_plans[0].package.value.size, 1)

    def test_delivery_option(self):
        self.assertEqual(self.do.customer_deliveries[0].package_delivery_plans[0].package.value.size, 1)

    def test_delivery_request(self):
        self.assertFalse(self.dr.time_window.since > self.dr.time_window.until)
        self.assertEqual(self.dr.priority, 10)
        self.assertEqual(
            self.dr.delivery_options[0].customer_deliveries[0].package_delivery_plans[0].package.value.size, 1)
