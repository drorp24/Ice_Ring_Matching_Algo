import unittest
from random import Random

from common.entities.drone_loading_station import DroneLoadingStation, DroneLoadingStationDistribution
from geometry.geo_distribution import UniformPointInBboxDistribution


class BasicDroneLoadingStationGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.num_of_drone_stations = 10

    def test_drone_loading_station_generation(self):
        drone_loading_station_distribution = DroneLoadingStationDistribution()
        stations = drone_loading_station_distribution.choose_rand(random=Random(100), amount=self.num_of_drone_stations)
        self.assertEqual(len(stations), 10)
        self.assertIsInstance(stations[0], DroneLoadingStation)

    def test_drone_loading_station_location(self):
        drone_loading_station_distribution = DroneLoadingStationDistribution(UniformPointInBboxDistribution(5, 10, 5, 10))
        stations = drone_loading_station_distribution.choose_rand(random=Random(100), amount=self.num_of_drone_stations)
        for station in stations:
            self.assertGreaterEqual(station.location.x, 5)
            self.assertLessEqual(station.location.x, 10)
            self.assertGreaterEqual(station.location.y, 5)
            self.assertLessEqual(station.location.y, 10)

