import math
import unittest

from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_vector_2d

EPSILON: float = 0.001


class BasicAngleMathTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a1 = Angle(90, AngleUnit.DEGREE)
        cls.a2 = Angle(0.25 * math.pi, AngleUnit.RADIAN)

    def test_2_angles_equal(self):
        self.assertEqual(self.a1, Angle(90, AngleUnit.DEGREE))

    def test_2_angles_not_equal(self):
        self.assertNotEqual(self.a1, Angle(91, AngleUnit.DEGREE))

    def test_convert_to_degree(self):
        self.assertEqual(self.a2.degrees(), 45)
        self.assertEqual(self.a1.degrees(), 90)

    def test_convert_to_radians(self):
        self.assertEqual(self.a1.radians(), 0.5 * math.pi)
        self.assertEqual(self.a2.radians(), 0.25 * math.pi)

    def test_convert_to_direction(self):
        self.assertAlmostEqual(self.a1.to_direction().norm, 1, EPSILON)
        self.assertAlmostEqual(self.a1.to_direction().dot(create_vector_2d(0, 1)), 1, EPSILON)

    def test_large_angle(self):
        self.assertEqual(Angle(810, AngleUnit.DEGREE), Angle(90, AngleUnit.DEGREE))

    def test_negative_angle(self):
        self.assertEqual(Angle(180, AngleUnit.DEGREE), Angle(-math.pi, AngleUnit.RADIAN))

    def test_reverse(self):
        self.assertEqual(Angle(90, AngleUnit.DEGREE).calc_reverse(), Angle(270, AngleUnit.DEGREE))

    def test_abs_difference(self):
        angle_diff_1 = Angle(90, AngleUnit.DEGREE).calc_abs_difference(Angle(200, AngleUnit.DEGREE))
        angle_diff_1_backwards = Angle(200, AngleUnit.DEGREE).calc_abs_difference(Angle(90, AngleUnit.DEGREE))
        self.assertEqual(angle_diff_1, Angle(110, AngleUnit.DEGREE))
        self.assertEqual(angle_diff_1, angle_diff_1_backwards)

