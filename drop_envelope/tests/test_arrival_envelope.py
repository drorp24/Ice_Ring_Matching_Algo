import unittest
from math import cos, pi, sin

from common.math.angle import Angle, AngleUnit
from drop_envelope.arrival_envelope import ArrivalEnvelope
from geometry.geo_factory import create_point_2d, create_vector_2d
from visualization.basic.pltdrawer2d import create_drawer_2d


class BasicArrivalEnvelopeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.arrival_azimuth = Angle(value=90, unit=AngleUnit.DEGREE)
        cls.maneuver_angle = Angle(value=90, unit=AngleUnit.DEGREE)
        cls.centroid = create_point_2d(x=0, y=0)
        cls.radius = 10
        cls.resolution = 3

    def test_from_maneuver_angle(self):
        arrival_envelope = ArrivalEnvelope.from_maneuver_angle(arrival_azimuth=self.arrival_azimuth,
                                                               radius=self.radius,
                                                               centroid=self.centroid,
                                                               maneuver_angle=self.maneuver_angle,
                                                               resolution_parameter=self.resolution)
        expected_repr_point = self.centroid.add_vector(
            create_vector_2d(x=self.radius * cos(self.arrival_azimuth.radians + pi),
                             y=self.radius * sin(self.arrival_azimuth.radians + pi)))
        self.assertEqual(len(arrival_envelope.maneuver_polygon.points), 2*(self.resolution + 1))
        self.assertEqual(arrival_envelope.arrival_azimuth, self.arrival_azimuth)
        self.assertAlmostEqual(arrival_envelope.repr_point, expected_repr_point)


