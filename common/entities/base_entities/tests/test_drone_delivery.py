import unittest
from datetime import datetime
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import DroneDelivery, EmptyDroneDelivery
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormations, DroneFormationType, PackageConfigurationOption
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution


class BasicDroneDeliveryGenerationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr = DeliveryRequestDistribution().choose_rand(random=Random(42), amount={DeliveryRequest: 3})

        cls.empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        cls.empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
            DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))

        cls.drone_delivery_1 = DroneDelivery(cls.empty_drone_delivery_1.id,
                                             cls.empty_drone_delivery_1.drone_formation,
                                             datetime(2020, 1, 23, 11, 30, 00), [cls.dr[0], cls.dr[1]])

        cls.drone_delivery_2 = DroneDelivery(cls.empty_drone_delivery_2.id,
                                             cls.empty_drone_delivery_2.drone_formation,
                                             datetime(2020, 1, 23, 12, 30, 00), [cls.dr[2]])

        cls.empty_drone_delivery_board = EmptyDroneDeliveryBoard(
            [cls.empty_drone_delivery_1, cls.empty_drone_delivery_2])

        cls.drone_delivery_board = DroneDeliveryBoard([cls.drone_delivery_1, cls.drone_delivery_2])

    def test_delivery_requests_quantity(self):
        self.assertGreaterEqual(len(self.dr), 3)

    def test_empty_drone_delivery(self):
        self.assertEqual(self.empty_drone_delivery_1.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.empty_drone_delivery_2.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))

    def test_drone_delivery(self):
        self.assertEqual(self.drone_delivery_1.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.drone_delivery_1.attack_time, datetime(2020, 1, 23, 11, 30, 00))
        self.assertEqual(len(self.drone_delivery_1.delivery_requests), 2)

        self.assertEqual(self.drone_delivery_2.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.drone_delivery_2.attack_time, datetime(2020, 1, 23, 12, 30, 00))
        self.assertEqual(len(self.drone_delivery_2.delivery_requests), 1)

    def test_empty_drone_delivery_board(self):
        self.assertEqual(len(self.empty_drone_delivery_board.empty_drone_deliveries), 2)
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[1].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES,
                             DroneType.drone_type_1))

    def test_drone_delivery_board(self):
        self.assertEqual(len(self.drone_delivery_board.drone_deliveries), 2)
        self.assertEqual(self.drone_delivery_board.drone_deliveries[0].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.drone_delivery_board.drone_deliveries[1].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
