import unittest
from math import cos, pi, sin

from common.math.angle import Angle, AngleUnit
from drop_envelope.arrival_envelope import ArrivalEnvelope, PotentialArrivalEnvelope, calc_cost
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
        self.assertEqual(len(arrival_envelope.maneuver_polygon.points), 2 * (self.resolution + 1))
        self.assertEqual(arrival_envelope.arrival_azimuth, self.arrival_azimuth)
        self.assertAlmostEqual(arrival_envelope.repr_point, expected_repr_point)

    def test_potential_arrival_envelope(self):
        arrival_azimuths = list(map(lambda value: Angle(value=value, unit=AngleUnit.DEGREE), list(range(0, 360, 45))))
        arrival_envelopes = list(map(lambda arrival_azimuth: ArrivalEnvelope.from_maneuver_angle(centroid=self.centroid,
                                                                                                 radius=self.radius,
                                                                                                 arrival_azimuth=
                                                                                                 arrival_azimuth,
                                                                                                 maneuver_angle=
                                                                                                 self.maneuver_angle),
                                     arrival_azimuths))
        potential_arrival_envelope = PotentialArrivalEnvelope(arrival_envelopes=arrival_envelopes,
                                                              centroid=self.centroid)
        self.assertEqual(len(range(0, 360, 45)), len(potential_arrival_envelope.arrival_envelopes))
        self.assertEqual(self.centroid, potential_arrival_envelope.centroid)
        self.assertEqual(arrival_envelopes[0], potential_arrival_envelope.arrival_envelopes[arrival_azimuths[0]])
        self.assertEqual(arrival_envelopes[1], potential_arrival_envelope.arrival_envelopes[arrival_azimuths[1]])
        self.assertEqual(arrival_envelopes[2], potential_arrival_envelope.arrival_envelopes[arrival_azimuths[2]])
        self.assertEqual(arrival_envelopes[3], potential_arrival_envelope.arrival_envelopes[arrival_azimuths[3]])

    def test_cal_cost(self):
        arrival_azimuths_1 = list(map(lambda value: Angle(value=value, unit=AngleUnit.DEGREE), list(range(0, 360, 45))))
        arrival_envelopes_1 = list(
            map(lambda arrival_azimuth: ArrivalEnvelope.from_maneuver_angle(centroid=self.centroid,
                                                                            radius=self.radius,
                                                                            arrival_azimuth=
                                                                            arrival_azimuth,
                                                                            maneuver_angle=
                                                                            self.maneuver_angle),
                arrival_azimuths_1))
        potential_arrival_envelope_1 = PotentialArrivalEnvelope(arrival_envelopes=arrival_envelopes_1,
                                                                centroid=self.centroid)

        arrival_azimuths_2 = list(map(lambda value: Angle(value=value, unit=AngleUnit.DEGREE), list(range(0, 360, 45))))
        arrival_envelopes_2 = list(
            map(lambda arrival_azimuth: ArrivalEnvelope.from_maneuver_angle(centroid=create_point_2d(0,100),
                                                                            radius=self.radius,
                                                                            arrival_azimuth=
                                                                            arrival_azimuth,
                                                                            maneuver_angle=
                                                                            self.maneuver_angle),
                arrival_azimuths_2))
        potential_arrival_envelope_2 = PotentialArrivalEnvelope(arrival_envelopes=arrival_envelopes_2,
                                                                centroid=self.centroid)
        cost = calc_cost(potential_arrival_envelope_1, potential_arrival_envelope_2)
        self.assertAlmostEqual(cost, 100)
