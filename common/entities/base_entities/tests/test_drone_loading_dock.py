import unittest
from random import Random

from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_id import EntityID
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
        self.assertIsInstance(docks[0].id, EntityID)
