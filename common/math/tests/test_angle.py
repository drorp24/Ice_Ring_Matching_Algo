import unittest
import math
from common.math.angle import Angle, _AngleUnit


class BasicAngleMathTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a1 = Angle(90)
        cls.a2 = Angle(0.25 * math.pi, unit=_AngleUnit.RADIAN)

    def test_conversion(self):
        self.assertEqual(self.a1.convert_to_radians(), 0.5 * math.pi)
        self.assertEqual(self.a2.convert_to_degrees(), 45)
        self.assertEqual(self.a1.convert_to_degrees(), 90)
        self.assertEqual(self.a2.convert_to_radians(), 0.25 * math.pi)
