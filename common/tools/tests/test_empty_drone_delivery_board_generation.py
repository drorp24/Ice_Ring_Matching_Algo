from common.tools.empty_drone_delivery_board_generation import generate_empty_delivery_board
import unittest
from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.drone_formation import DroneFormation
from common.tools.fleet_reader import FleetReader
from common.tools.tests.path_utils import create_path_from_current_directory, Path


class TestEmptyDroneDeliveryBoardGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fleet_reader = FleetReader(create_path_from_current_directory(Path('TestFleet.json')))

    def test_empty_drone_delivery_board(self):
        empty_drone_delivery_board = generate_empty_delivery_board(self.fleet_reader)
        self.assertIsInstance(empty_drone_delivery_board, EmptyDroneDeliveryBoard)
        self.assertEqual(len(empty_drone_delivery_board.empty_drone_deliveries), 24)
        self.assertIsInstance(empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation, DroneFormation)
