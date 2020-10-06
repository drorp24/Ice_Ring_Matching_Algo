import unittest
import math
from common.math.angle import create_degree_angle, create_radian_angle


class BasicAngleMathTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a1 = create_degree_angle(90)
        cls.a2 = create_radian_angle(0.25 * math.pi)

    def test_convert_to_degree(self):
        self.assertEqual(self.a2.convert_to_degrees(), 45)
        self.assertEqual(self.a1.convert_to_degrees(), 90)

    def test_convert_to_radians(self):
        self.assertEqual(self.a1.convert_to_radians(), 0.5 * math.pi)
        self.assertEqual(self.a2.convert_to_radians(), 0.25 * math.pi)
