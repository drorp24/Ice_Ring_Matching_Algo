import unittest
import math
from common.math.angle import Angle, AngleUnit


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
        self.assertEqual(self.a2.in_degrees(), 45)
        self.assertEqual(self.a1.in_degrees(), 90)

    def test_convert_to_radians(self):
        self.assertEqual(self.a1.in_radians(), 0.5 * math.pi)
        self.assertEqual(self.a2.in_radians(), 0.25 * math.pi)
