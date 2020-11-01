import unittest

from common.entities.package import PackageType
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle, AngleUnit
from geometry.geo2d import Polygon2D
from geometry.geo_factory import create_point_2d, create_polygon_2d_from_ellipse, create_empty_geometry_2d
from services.mock_envelope_services import MockEnvelopeServices


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
        cls.drop_envelope_service = MockEnvelopeServices()

    def test_package_weights(self):
        self.assertEqual(PackageType.TINY.value.weight, 1)
        self.assertEqual(PackageType.SMALL.value.weight, 2)
        self.assertEqual(PackageType.MEDIUM.value.weight, 4)
        self.assertEqual(PackageType.LARGE.value.weight, 8)

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
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(-821.72, -473),
                                                           ellipse_width=100,
                                                           ellipse_height=100,
                                                           ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_envelope = self.drop_envelope_service.drop_envelope(self.pdp.package_type, drone_azimuth,
                                                                   self.pdp.drop_point, self.pdp.azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_drop_envelope_when_drop_and_drone_azimuth_delta_45_deg(self):
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(-244.87, -915.63),
                                                           ellipse_width=100,
                                                           ellipse_height=70.71,
                                                           ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_envelope = self.drop_envelope_service.drop_envelope(self.pdp.package_type, drone_azimuth, self.pdp.drop_point,
                                                 self.pdp.azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_drop_envelope_when_drop_and_drone_azimuth_delta_100_deg(self):
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 100, AngleUnit.DEGREE)
        actual_envelope = self.drop_envelope_service.drop_envelope(self.pdp.package_type, drone_azimuth, self.pdp.drop_point,
                                                 self.pdp.azimuth)
        self.assertEqual(actual_envelope, create_empty_geometry_2d())

    def test_delivery_envelope_when_same_drop_and_drone_azimuth(self):
        drone_location = create_point_2d(-821.72, -473)
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees(), AngleUnit.DEGREE)
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(1, 2),
                                                           ellipse_width=100,
                                                           ellipse_height=100,
                                                           ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_envelope = self.drop_envelope_service.delivery_envelope(self.pdp.package_type, drone_location,
                                                                       drone_azimuth, self.pdp.azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_delivery_envelope_when_drop_and_drone_azimuth_delta_45_deg(self):
        drone_location = create_point_2d(-244.87, -915.63)
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(1, 2),
                                                           ellipse_width=100,
                                                           ellipse_height=70.71,
                                                           ellipse_rotation_deg=drone_azimuth.in_degrees())
        actual_envelope = self.drop_envelope_service.delivery_envelope(self.pdp.package_type, drone_location,
                                                                       drone_azimuth, self.pdp.azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_delivery_envelope_when_drop_and_drone_azimuth_delta_91_deg(self):
        drone_location = create_point_2d(0, 0)
        drone_azimuth = Angle(self.pdp.azimuth.in_degrees() + 91, AngleUnit.DEGREE)
        actual_envelope = self.drop_envelope_service.delivery_envelope(self.pdp.package_type, drone_location,
                                                                       drone_azimuth, self.pdp.azimuth)
        self.assertEqual(actual_envelope, create_empty_geometry_2d())

    def assertThatEnvelopesAreApproximatelyEqual(self, actual_envelope: Polygon2D, expected_envelope: Polygon2D):
        epsilon_value = 0.001
        actual_drop_area = actual_envelope.calc_area()
        expected_drop_area = expected_envelope.calc_area()
        relative_epsilon_area = expected_drop_area * epsilon_value
        self.assertGreaterEqual(min(actual_drop_area, expected_drop_area) /
                                max(actual_drop_area, expected_drop_area), 1 - epsilon_value)
        self.assertGreaterEqual(actual_drop_area, relative_epsilon_area)
        self.assertLessEqual(expected_envelope.calc_difference(actual_envelope).calc_area(), relative_epsilon_area)
        self.assertLessEqual(actual_envelope.calc_difference(expected_envelope).calc_area(), relative_epsilon_area)
