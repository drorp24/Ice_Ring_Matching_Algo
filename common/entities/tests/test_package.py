import unittest

from common.entities.package import PackageType, Package
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d, create_polygon_2d_from_ellipsis
from geometry.shapely_wrapper import _ShapelyEmptyGeometry


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = Package(PackageType.TINY)
        cls.p2 = Package(PackageType.SMALL)
        cls.p3 = Package(PackageType.MEDIUM)
        cls.p4 = Package(PackageType.LARGE)
        point = create_point_2d(1, 2)
        cls.pdp = package_delivery_plan_factory(point,
                                                azimuth=Angle(30, AngleUnit.DEGREE),
                                                elevation=Angle(80, AngleUnit.DEGREE),
                                                package_type=PackageType.TINY)

    def test_package_type(self):
        self.assertEqual(self.p1.type.value, 1)
        self.assertEqual(self.p2.type.value, 2)
        self.assertEqual(self.p3.type.value, 4)
        self.assertEqual(self.p4.type.value, 8)

    def test_package_delivery_plan(self):
        self.assertEqual(self.pdp.package.type.value, 1)

    def test_drop_envelope_when_same_drop_and_drone_azimuth(self):
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees(), AngleUnit.DEGREE)
        expected_drop_envelope = create_polygon_2d_from_ellipsis(ellipsis_center=(-821.7241335952167,
                                                                                  -473.0000000000001),
                                                                 ellipsis_width=100,
                                                                 ellipsis_height=100,
                                                                 ellipsis_rotation=drone_azimuth.in_degrees())
        actual_drop_envelope = self.pdp.drop_envelope(drone_azimuth)
        expected_difference = _ShapelyEmptyGeometry()
        actual_difference = actual_drop_envelope.calc_difference(expected_drop_envelope)
        self.assertEqual(expected_difference, actual_difference)

    def test_drop_envelope_when_drop_and_drone_azimuth_delta_45_deg(self):
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
        expected_drop_envelope = create_polygon_2d_from_ellipsis(ellipsis_center=(-244.87809284739458,
                                                                                  -915.6295349746149),
                                                                 ellipsis_width=100,
                                                                 ellipsis_height=70.71067811865474,
                                                                 ellipsis_rotation=drone_azimuth.in_degrees())
        actual_drop_envelope = self.pdp.drop_envelope(drone_azimuth)
        expected_difference = _ShapelyEmptyGeometry()
        actual_difference = actual_drop_envelope.calc_difference(expected_drop_envelope)
        self.assertEqual(expected_difference, actual_difference)
