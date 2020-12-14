import unittest
from random import Random

from common.entities.drone_loading_dock import DroneLoadingDock, DroneLoadingDockDistribution


class BasicDroneLoadingDockGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.num_of_drone_docks = 10

    def test_drone_loading_dock_generation(self):
        drone_loading_dock_distribution = DroneLoadingDockDistribution()
        docks = drone_loading_dock_distribution.choose_rand(random=Random(100), amount=self.num_of_drone_docks)
        self.assertEqual(len(docks), self.num_of_drone_docks)
        self.assertIsInstance(docks[0], DroneLoadingDock)
