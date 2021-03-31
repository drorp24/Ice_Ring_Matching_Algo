import unittest
from random import Random
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.math.angle import Angle, AngleUnit
from drop_envelope.azimuth_quantization import get_azimuth_quantization_values
from drop_envelope.loading_dock_envelope import LoadingDockPotentialEnvelope
from drop_envelope.slide_service import MockSlidesServiceWrapper
from visualization.basic.color import Color
from visualization.basic.pltdrawer2d import create_drawer_2d


class BasicLoadingDockEnvelope(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loading_dock_distribution = DroneLoadingDockDistribution()

    def base_location_plot(self):
        drawer = create_drawer_2d()
        dock = self.loading_dock_distribution.choose_rand(Random(10), amount=1)[0]
        loading_dock_potential_envelope = LoadingDockPotentialEnvelope(drone_loading_dock=dock)
        potential_arrival_envelope = loading_dock_potential_envelope.get_potential_arrival_envelope(
            get_azimuth_quantization_values(MockSlidesServiceWrapper.drone_azimuth_level_amount),
            maneuver_angle=Angle(value=90, unit=AngleUnit.DEGREE))
        for arrival_angle in (potential_arrival_envelope.arrival_envelopes.keys()):
            arrival_direction = arrival_angle.calc_reverse().to_direction() * 5
            drawer.add_arrow2d(
                tail=potential_arrival_envelope.get_arrival_envelope(arrival_angle).repr_point.add_vector(
                    arrival_direction),
                head=potential_arrival_envelope.get_arrival_envelope(arrival_angle).repr_point, facecolor=Color.Red,
                edgecolor=Color.Red)
            drawer.add_point2d(point2d=potential_arrival_envelope.get_arrival_envelope(arrival_angle).repr_point,
                               facecolor=Color.Red, edgecolor=Color.Red)
        drawer.draw()
        self.assertLess(loading_dock_potential_envelope.loading_dock.drone_loading_station.location.x, 100)
        self.assertLess(loading_dock_potential_envelope.loading_dock.drone_loading_station.location.y, 100)

    def test_loading_dock_potential_envelope_creation(self):
        dock = self.loading_dock_distribution.choose_rand(Random(12), amount=1)[0]
        loading_dock_potential_envelope = LoadingDockPotentialEnvelope(drone_loading_dock=dock)
        potential_arrival_envelope = loading_dock_potential_envelope.get_potential_arrival_envelope(
            get_azimuth_quantization_values(MockSlidesServiceWrapper.drone_azimuth_level_amount),
            maneuver_angle=Angle(value=90, unit=AngleUnit.DEGREE))
        self.assertAlmostEqual(loading_dock_potential_envelope.loading_dock.drone_loading_station.location.x, 47.45706,
                               delta=0.01)
        self.assertAlmostEqual(loading_dock_potential_envelope.loading_dock.drone_loading_station.location.y, 65.74725,
                               delta=0.01)
        self.assertAlmostEqual(loading_dock_potential_envelope.get_centroid().x, 47.45706, delta=0.01)
        self.assertAlmostEqual(loading_dock_potential_envelope.get_centroid().y, 65.74725, delta=0.01)
        self.assertEqual(len(potential_arrival_envelope.arrival_envelopes), 8)
        self.assertAlmostEqual(list(potential_arrival_envelope.arrival_envelopes.values())[0].repr_point.x, 47.45706,
                               delta=0.01)
        self.assertAlmostEqual(list(potential_arrival_envelope.arrival_envelopes.values())[0].repr_point.y, 65.74725,
                               delta=0.01)
