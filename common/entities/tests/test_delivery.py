import unittest
from datetime import datetime

from time_window import TimeWindow

from common.entities.delivery_requests_factory import create_delivery_requests_from_file


class BasicDeliveryGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # point = create_point_2d(1, 2)
        #
        # cls.cd = create_customer_delivery(point, azimuth=Angle(30), elevation=Angle(80),
        #                                   package=PackageType.TINY)
        # cls.do = create_delivery_option(point, azimuth=Angle(30), elevation=Angle(80),
        #                                 package=PackageType.TINY)
        #
        # cls.time_window = TimeWindow(datetime(2020, 1, 23, 11, 30, 00),
        #                              datetime(2020, 1, 23, 11, 35, 00))


        cls.dr = create_delivery_requests_from_file('DeliveryRequestTest.json')

    def test_customer_delivery(self):
        self.assertEqual(len(self.dr[0].delivery_options[0].customer_deliveries), 1)
        self.assertEqual(
            self.dr[0].delivery_options[0].customer_deliveries[0].package_delivery_plans[0].package.value.size, 1)

    def test_delivery_option(self):
        self.assertEqual(len(self.dr[0].delivery_options), 2)

    def test_delivery_request(self):
        self.assertEqual(len(self.dr), 2)
        self.assertFalse(self.dr[0].time_window.since > self.dr[0].time_window.until)
        self.assertEqual(self.dr[0].priority, 10)
        self.assertEqual(
            self.dr[0].delivery_options[0].customer_deliveries[0].package_delivery_plans[0].package.value.size, 1)
