import unittest
from collections import Counter
from pprint import pprint
from random import Random

from common.entities.disribution.test.test_distribution import assert_samples_approx_expected
from common.entities.package import PackageType, PackageDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle, AngleUnit
from geometry.geo2d import Polygon2D
from geometry.geo_factory import create_point_2d, create_polygon_2d_from_ellipse, create_empty_geometry_2d


class BasicPackageTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = PackageType.TINY
        cls.p2 = PackageType.SMALL
        cls.p3 = PackageType.MEDIUM
        cls.p4 = PackageType.LARGE
        point = create_point_2d(1, 2)
        cls.pdp = PackageDeliveryPlan(point,
                                      azimuth=Angle(30, AngleUnit.DEGREE),
                                      pitch=Angle(80, AngleUnit.DEGREE),
                                      package_type=PackageType.TINY)

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
        expected_pdp = PackageDeliveryPlan(create_point_2d(1, 2),
                                           azimuth=Angle(30, AngleUnit.DEGREE),
                                           pitch=Angle(80, AngleUnit.DEGREE),
                                           package_type=PackageType.TINY)
        self.assertEqual(self.pdp, expected_pdp)

    def test_2_package_delivery_plans_not_equal(self):
        expected_pdp = PackageDeliveryPlan(create_point_2d(1, 2),
                                           azimuth=Angle(31, AngleUnit.DEGREE),
                                           pitch=Angle(80, AngleUnit.DEGREE),
                                           package_type=PackageType.TINY)
        self.assertNotEqual(self.pdp, expected_pdp)

    def test_drop_envelope_when_same_drop_and_drone_azimuth(self):
        drone_azimuth = Angle(self.pdp.azimuth.degrees, AngleUnit.DEGREE)
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(-821.72, -473),
                                                           ellipse_width=100,
                                                           ellipse_height=100,
                                                           ellipse_rotation_deg=drone_azimuth.degrees)
        actual_envelope = self.pdp.calc_drop_envelope(drone_azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_drop_envelope_when_drop_and_drone_azimuth_delta_45_deg(self):
        drone_azimuth = Angle(self.pdp.azimuth.degrees + 45, AngleUnit.DEGREE)
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(-244.87, -915.63),
                                                           ellipse_width=100,
                                                           ellipse_height=70.71,
                                                           ellipse_rotation_deg=drone_azimuth.degrees)
        actual_envelope = self.pdp.calc_drop_envelope(drone_azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_drop_envelope_when_drop_and_drone_azimuth_delta_100_deg(self):
        drone_azimuth = Angle(self.pdp.azimuth.degrees + 100, AngleUnit.DEGREE)
        actual_envelope = self.pdp.calc_drop_envelope(drone_azimuth)
        self.assertEqual(actual_envelope, create_empty_geometry_2d())

    def test_delivery_envelope_when_same_drop_and_drone_azimuth(self):
        drone_location = create_point_2d(-821.72, -473)
        drone_azimuth = Angle(self.pdp.azimuth.degrees, AngleUnit.DEGREE)
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(1, 2),
                                                           ellipse_width=100,
                                                           ellipse_height=100,
                                                           ellipse_rotation_deg=drone_azimuth.degrees)
        actual_envelope = self.pdp.calc_delivery_envelope(drone_location, drone_azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_delivery_envelope_when_drop_and_drone_azimuth_delta_45_deg(self):
        drone_location = create_point_2d(-244.87, -915.63)
        drone_azimuth = Angle(self.pdp.azimuth.degrees + 45, AngleUnit.DEGREE)
        expected_envelope = create_polygon_2d_from_ellipse(ellipse_center=create_point_2d(1, 2),
                                                           ellipse_width=100,
                                                           ellipse_height=70.71,
                                                           ellipse_rotation_deg=drone_azimuth.degrees)
        actual_envelope = self.pdp.calc_delivery_envelope(drone_location, drone_azimuth)
        self.assertThatEnvelopesAreApproximatelyEqual(actual_envelope, expected_envelope)

    def test_delivery_envelope_when_drop_and_drone_azimuth_delta_91_deg(self):
        drone_location = create_point_2d(0, 0)
        drone_azimuth = Angle(self.pdp.azimuth.degrees + 91, AngleUnit.DEGREE)
        actual_envelope = self.pdp.calc_delivery_envelope(drone_location, drone_azimuth)
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


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.pd = PackageDistribution({PackageType.TINY.name: 0.8, PackageType.SMALL.name: 0.4})

    def test_probability_of_package_generation_is_correct(self):
        rand_samples = 10000
        values_random_sample = list(map(lambda i: self.pd.choose_rand(Random(i))[0].name, range(rand_samples)))
        sample_count = dict(Counter(values_random_sample))
        expected_prob = {PackageType.TINY.name: 0.66,
                         PackageType.SMALL.name: 0.33,
                         PackageType.MEDIUM.name: 0.0,
                         PackageType.LARGE.name: 0.0}

        for package in PackageType.get_all_names():
            assert_samples_approx_expected(self, package, expected_prob, sample_count)

    def print_example_package(self):
        pprint(PackageType.TINY)