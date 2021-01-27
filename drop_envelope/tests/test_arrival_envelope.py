import unittest
from common.math.angle import Angle, AngleUnit


class BasicArrivalEnvelopeTestCase(unittest.TestCase):
    def setUpClass(cls) -> None:
        cls.arrival_azimuth = Angle(value=90, unit=AngleUnit.DEGREE)
