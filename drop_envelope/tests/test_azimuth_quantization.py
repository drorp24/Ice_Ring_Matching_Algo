import unittest

from drop_envelope.azimuth_quantization import *


class BasicQuantizationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.drop_azimuth_amount = 8
        cls.drone_azimuth_amount = 10

    def test_get_azimuth_values(self):
        drop_values = get_azimuth_quantization_values(self.drop_azimuth_amount)
        drone_values = get_azimuth_quantization_values(self.drone_azimuth_amount)
        self.assertEqual(drop_values[0], Angle(value=0, unit=AngleUnit.DEGREE))
        self.assertEqual(drop_values[1], Angle(value=45, unit=AngleUnit.DEGREE))
        self.assertEqual(len(drop_values), 8)
        self.assertEqual(len(drone_values), 10)
        self.assertEqual(drone_values[0], Angle(value=0, unit=AngleUnit.DEGREE))
        self.assertEqual(drone_values[1], Angle(value=36, unit=AngleUnit.DEGREE))

    def test_get_azimuth_quantization(self):
        self.assertEqual(get_azimuth_quantization_value(Angle(value=60, unit=AngleUnit.DEGREE)),
                         Angle(value=45, unit=AngleUnit.DEGREE))
        self.assertEqual(get_azimuth_quantization_value(Angle(value=95, unit=AngleUnit.DEGREE)),
                         Angle(value=90, unit=AngleUnit.DEGREE))
