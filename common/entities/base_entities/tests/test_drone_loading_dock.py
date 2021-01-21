import unittest
from random import Random

from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution


class BasicDroneLoadingDockGenerationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.num_of_drone_docks = 10

    def test_drone_loading_dock_generation(self):
        drone_loading_dock_distribution = DroneLoadingDockDistribution()
        docks = drone_loading_dock_distribution.choose_rand(random=Random(100), amount=self.num_of_drone_docks)
        self.assertEqual(len(docks), self.num_of_drone_docks)
        self.assertIsInstance(docks[0], DroneLoadingDock)

    def test_drone_loading_dock_as_shapeable_collection(self):
        drone_loading_dock_distribution = DroneLoadingDockDistribution()
        dock = drone_loading_dock_distribution.choose_rand(random=Random(100), amount=1)[0]
        self.assertEqual(dock.shapeabls(), [dock.drone_loading_station])
        self.assertEqual(dock.centroid(), dock.drone_loading_station.location)
