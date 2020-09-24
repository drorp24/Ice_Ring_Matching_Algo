import unittest

from common.entities.package import PackageType
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle
from geometry.geo_factory import create_point_2d


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = PackageType.TINY
        cls.p2 = PackageType.SMALL
        cls.p3 = PackageType.MEDIUM
        cls.p4 = PackageType.LARGE
        point = create_point_2d(1,2)
        cls.pdp = package_delivery_plan_factory(point, azimuth=Angle(30), elevation=Angle(80),
                                                package=PackageType.TINY)

    def test_package_type(self):
        self.assertEqual(self.p1.value.size, 1)
        self.assertEqual(self.p2.value.size, 2)
        self.assertEqual(self.p3.value.size, 4)
        self.assertEqual(self.p4.value.size, 8)

    def test_package_delivery_plan(self):
        self.assertEqual(self.pdp.package.value.size, 1)
