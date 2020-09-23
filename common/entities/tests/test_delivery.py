import unittest

from common.entities.delivery_factory import create_customer_delivery, create_delivery_option, create_delivery_request
from common.entities.package_factory import package_factory, package_delivery_plan_factory


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = package_factory("Tiny")
        cls.p2 = package_factory("Small")
        cls.p3 = package_factory("Medium")
        cls.p4 = package_factory("Large")
        cls.p5 = package_factory("mini")
        cls.pdp = package_delivery_plan_factory(x=0, y=0, arrival_angle=0.1, hitting_angle=1.81, package_type="Tiny")
        cls.cd = create_customer_delivery(x=0, y=0, azimuth=0.1, elevation=1.81, package_type="Tiny")
        cls.do = create_delivery_option(x=0, y=0, azimuth=0.1, elevation=1.81, package_type="Tiny")
        cls.dr = create_delivery_request(x=0, y=0, azimuth=0.1, elevation=1.81, package_type="Tiny",
                                         since_time=1600847749, until_time=1600851349, priority=10)

    def test_package_type(self):
        self.assertEqual(self.p1.type(), "Tiny")
        self.assertEqual(self.p2.type(), "Small")
        self.assertEqual(self.p3.type(), "Medium")
        self.assertEqual(self.p4.type(), "Large")
        self.assertEqual(self.p5, None)

    def test_package_delivery_plan(self):
        self.assertEqual(self.pdp.package.type(), "Tiny")

    def test_customer_delivery(self):
        self.assertEqual(self.cd.type, "CustomerDelivery")
        self.assertEqual(self.cd.package_delivery_plans[0].package.type(), "Tiny")

    def test_delivery_option(self):
        self.assertEqual(self.do.type, "DeliveryOption")
        self.assertEqual(self.do.customer_deliveries[0].type, "CustomerDelivery")
        self.assertEqual(self.do.customer_deliveries[0].package_delivery_plans[0].package.type(), "Tiny")

    def test_delivery_request(self):
        self.assertEqual(self.dr.type, "DeliveryRequest")
        self.assertEqual(self.dr.since_time, 1600847749)
        self.assertEqual(self.dr.until_time, 1600851349)
        self.assertEqual(self.dr.priority, 10)
        self.assertEqual(self.dr.delivery_options[0].type, "DeliveryOption")
        self.assertEqual(self.dr.delivery_options[0].customer_deliveries[0].type, "CustomerDelivery")
        self.assertEqual(self.dr.delivery_options[0].customer_deliveries[0].package_delivery_plans[0].package.type(),
                         "Tiny")

