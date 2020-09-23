import unittest

from common.entities.package_factory import package_factory, package_delivery_plan_factory


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = package_factory("Tiny")
        cls.p2 = package_factory("Small")
        cls.p3 = package_factory("Medium")
        cls.p4 = package_factory("Large")
        cls.p5 = package_factory("mini")
        cls.pdp = package_delivery_plan_factory(x=0, y=0, azimuth=0.1, elevation=1.81, package_type="Tiny")

    def test_package_type(self):
        self.assertEqual(self.p1.type(), "Tiny")
        self.assertEqual(self.p2.type(), "Small")
        self.assertEqual(self.p3.type(), "Medium")
        self.assertEqual(self.p4.type(), "Large")
        self.assertEqual(self.p5, None)

    def test_package_delivery_plan(self):
        self.assertEqual(self.pdp.package.type(), "Tiny")


