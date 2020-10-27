import unittest

from common.entities.package import PackageType
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d, create_polygon_2d_from_ellipse, create_empty_geometry_2d

EQUAL_AREA_EPSILON_DECIMAL_PLACES: int = 5


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = PackageType.TINY
        cls.p2 = PackageType.SMALL
        cls.p3 = PackageType.MEDIUM
        cls.p4 = PackageType.LARGE
        point = create_point_2d(1, 2)
        cls.pdp = package_delivery_plan_factory(point,
                                                azimuth=Angle(30, AngleUnit.DEGREE),
                                                elevation=Angle(80, AngleUnit.DEGREE),
                                                package_type=PackageType.TINY)

    def test_package_size(self):
        self.assertEqual(self.p1.value.weight, 1)
        self.assertEqual(self.p2.value.weight, 2)
        self.assertEqual(self.p3.value.weight, 4)
        self.assertEqual(self.p4.value.weight, 8)

    def test_2_package_equal(self):
        self.assertEqual(self.p1.value, PackageType.TINY.value)

    def test_2_package_not_equal(self):
        self.assertNotEqual(self.p1.value, self.p2.value)

    def test_package_delivery_plan(self):
        self.assertEqual(self.pdp.package_type.value.weight, 1)

    def test_2_package_delivery_plans_equal(self):
        expected_pdp = package_delivery_plan_factory(create_point_2d(1, 2),
                                                     azimuth=Angle(30, AngleUnit.DEGREE),
                                                     elevation=Angle(80, AngleUnit.DEGREE),
                                                     package_type=PackageType.TINY)
        self.assertEqual(self.pdp, expected_pdp)

    def test_2_package_delivery_plans_not_equal(self):
        expected_pdp = package_delivery_plan_factory(create_point_2d(1, 2),
                                                     azimuth=Angle(31, AngleUnit.DEGREE),
                                                     elevation=Angle(80, AngleUnit.DEGREE),
                                                     package_type=PackageType.TINY)
        self.assertNotEqual(self.pdp, expected_pdp)

    def test_drop_envelope_when_same_drop_and_drone_azimuth(self):
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees(), AngleUnit.DEGREE)
        expected_drop_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(-821.72, -473),
                                                                ellipse_width=100,
                                                                ellipse_height=100,
                                                                ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_drop_envelope = self.pdp.drop_envelope(drone_azimuth)
        self.assertEqual(expected_drop_envelope, actual_drop_envelope)

    def test_drop_envelope_when_drop_and_drone_azimuth_delta_45_deg(self):
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
        expected_drop_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(-244.87, -915.63),
                                                                ellipse_width=100,
                                                                ellipse_height=70.71067811865474,
                                                                ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_drop_envelope = self.pdp.drop_envelope(drone_azimuth)
        actual_difference = actual_drop_envelope.calc_difference(expected_drop_envelope)
        expected_difference = create_empty_geometry_2d()
        self.assertAlmostEqual(expected_difference.calc_area(), actual_difference.calc_area(), EQUAL_AREA_EPSILON_DECIMAL_PLACES)

    def test_drop_envelope_when_drop_and_drone_azimuth_delta_100_deg(self):
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 100, AngleUnit.DEGREE)
        expected_drop_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(611.65, -725.74),
                                                                ellipse_width=100,
                                                                ellipse_height=0,
                                                                ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_drop_envelope = self.pdp.drop_envelope(drone_azimuth)
        actual_difference = actual_drop_envelope.calc_difference(expected_drop_envelope)
        expected_difference = create_empty_geometry_2d()
        self.assertAlmostEqual(expected_difference.calc_area(), actual_difference.calc_area(), EQUAL_AREA_EPSILON_DECIMAL_PLACES)

    def test_drop_envelope_when_drone_azimuth_is_negative(self):
        drone_azimuth = Angle(-10, AngleUnit.DEGREE)
        self.assertRaises(ValueError, self.pdp.drop_envelope, drone_azimuth)

    def test_drop_envelope_when_drone_azimuth_is_greater_than_360(self):
        drone_azimuth = Angle(400, AngleUnit.DEGREE)
        self.assertRaises(ValueError, self.pdp.drop_envelope, drone_azimuth)

    def test_delivery_envelope_when_same_drop_and_drone_azimuth(self):
        drone_location = create_point_2d(-821.7241335952167, -473.0000000000001)
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees(), AngleUnit.DEGREE)
        expected_delivery_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(1,2),
                                                                    ellipse_width=100,
                                                                    ellipse_height=100,
                                                                    ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_delivery_envelope = self.pdp.delivery_envelope(drone_location, drone_azimuth)
        actual_difference = actual_delivery_envelope.calc_difference(expected_delivery_envelope)
        expected_difference = create_empty_geometry_2d()
        self.assertAlmostEqual(expected_difference.calc_area(), actual_difference.calc_area(), EQUAL_AREA_EPSILON_DECIMAL_PLACES)

    def test_delivery_envelope_when_drop_and_drone_azimuth_delta_45_deg(self):
        drone_location = create_point_2d(-244.87, -915.63)
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
        expected_delivery_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(1, 2),
                                                                    ellipse_width=100,
                                                                    ellipse_height=70.71,
                                                                    ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_delivery_envelope = self.pdp.delivery_envelope(drone_location, drone_azimuth)
        actual_difference = actual_delivery_envelope.calc_difference(expected_delivery_envelope)
        expected_difference = create_empty_geometry_2d()
        self.assertAlmostEqual(expected_difference.calc_area(), actual_difference.calc_area(), EQUAL_AREA_EPSILON_DECIMAL_PLACES)

    def test_delivery_envelope_when_drop_and_drone_azimuth_delta_100_deg(self):
        drone_location = create_point_2d(611.65, -725.74)
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 100, AngleUnit.DEGREE)
        expected_delivery_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(1, 2),
                                                                    ellipse_width=100,
                                                                    ellipse_height=0,
                                                                    ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_delivery_envelope = self.pdp.delivery_envelope(drone_location, drone_azimuth)
        actual_difference = actual_delivery_envelope.calc_difference(expected_delivery_envelope)
        expected_difference = create_empty_geometry_2d()
        self.assertAlmostEqual(expected_difference.calc_area(), actual_difference.calc_area(), EQUAL_AREA_EPSILON_DECIMAL_PLACES)
