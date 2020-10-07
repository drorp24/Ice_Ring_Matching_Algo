import unittest

from common.entities.package import PackageType
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import create_degree_angle, create_radian_angle
from geometry.geo_factory import create_point_2d


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = PackageType.TINY
        cls.p2 = PackageType.SMALL
        cls.p3 = PackageType.MEDIUM
        cls.p4 = PackageType.LARGE
        point = create_point_2d(1,2)
        cls.pdp = package_delivery_plan_factory(point, azimuth=create_degree_angle(30), elevation=create_degree_angle(80),
                                                package=PackageType.TINY)

    def test_package_size(self):
        self.assertEqual(self.p1.value.weight, 1)
        self.assertEqual(self.p2.value.weight, 2)
        self.assertEqual(self.p3.value.weight, 4)
        self.assertEqual(self.p4.value.weight, 8)

    def test_package_delivery_plan(self):
        self.assertEqual(self.pdp.package.weight, 1)
