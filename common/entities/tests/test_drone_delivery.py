import unittest
from datetime import datetime

from common.entities.delivery_requests_factory import create_delivery_requests_from_file
from common.entities.drone_delivery import DroneDelivery, EmptyDroneDelivery
from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard
from common.entities.drone_formation import DroneFormationType


class BasicDroneDeliveryGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr = create_delivery_requests_from_file('DeliveryRequestTest.json')

        cls.empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormationType._2X_PLATFORM_1_2X8)
        cls.empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormationType._4X_PLATFORM_1_2X8)

        cls.drone_delivery_1 = DroneDelivery(cls.empty_drone_delivery_1.identity,
                                             cls.empty_drone_delivery_1.drone_formation_type,
                                             datetime(2020, 1, 23, 11, 30, 00), [cls.dr[0], cls.dr[1]])

        cls.drone_delivery_2 = DroneDelivery(cls.empty_drone_delivery_2.identity,
                                             cls.empty_drone_delivery_2.drone_formation_type,
                                             datetime(2020, 1, 23, 12, 30, 00), [cls.dr[2]])

        cls.empty_drone_delivery_board = EmptyDroneDeliveryBoard(
            [cls.empty_drone_delivery_1, cls.empty_drone_delivery_2])

        cls.drone_delivery_board = DroneDeliveryBoard([cls.drone_delivery_1, cls.drone_delivery_2])

    def test_delivery_requests_quantity(self):
        self.assertGreaterEqual(len(self.dr), 3)

    def test_empty_drone_delivery(self):
        self.assertEqual(self.empty_drone_delivery_1.drone_formation_type, DroneFormationType._2X_PLATFORM_1_2X8)
        self.assertEqual(self.empty_drone_delivery_2.drone_formation_type, DroneFormationType._4X_PLATFORM_1_2X8)

    def test_drone_delivery(self):
        self.assertEqual(self.drone_delivery_1.drone_formation_type, DroneFormationType._2X_PLATFORM_1_2X8)
        self.assertEqual(self.drone_delivery_1.attack_time, datetime(2020, 1, 23, 11, 30, 00))
        self.assertEqual(len(self.drone_delivery_1.delivery_requests), 2)

        self.assertEqual(self.drone_delivery_2.drone_formation_type, DroneFormationType._4X_PLATFORM_1_2X8)
        self.assertEqual(self.drone_delivery_2.attack_time, datetime(2020, 1, 23, 12, 30, 00))
        self.assertEqual(len(self.drone_delivery_2.delivery_requests), 1)

    def test_empty_drone_delivery_board(self):
        self.assertEqual(len(self.empty_drone_delivery_board.empty_drone_deliveries), 2)
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation_type,
                         DroneFormationType._2X_PLATFORM_1_2X8)
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[1].drone_formation_type,
                         DroneFormationType._4X_PLATFORM_1_2X8)

    def test_drone_delivery_board(self):
        self.assertEqual(len(self.drone_delivery_board.drone_deliveries), 2)
        self.assertEqual(self.drone_delivery_board.drone_deliveries[0].drone_formation_type,
                         DroneFormationType._2X_PLATFORM_1_2X8)
        self.assertEqual(self.drone_delivery_board.drone_deliveries[1].drone_formation_type,
                         DroneFormationType._4X_PLATFORM_1_2X8)
