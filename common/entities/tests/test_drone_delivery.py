import unittest
from datetime import datetime

from input.delivery_requests_json_converter import create_delivery_requests_from_file
from common.entities.drone_delivery import DroneDelivery, EmptyDroneDelivery
from common.entities.drone_formation import DroneFormation, Configurations, DroneFormationOptions


class BasicDroneDeliveryGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.dr = create_delivery_requests_from_file('DeliveryRequestTest.json')

        cls.empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormationType._2X_PLATFORM_1_2X8)
        cls.empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormationType._4X_PLATFORM_1_2X8)

        cls.drone_delivery_1 = DroneDelivery(cls.empty_drone_delivery_1.identity, cls.empty_drone_delivery_1.drone_formation_type,
                                         datetime(2020, 1, 23, 11, 30, 00),[cls.dr[0],cls.dr[1]]),

        cls.drone_delivery_2 = DroneDelivery(cls.empty_drone_delivery_2.identity,
                                             cls.empty_drone_delivery_2.drone_formation_type,
                                             datetime(2020, 1, 23, 12, 30, 00), cls.dr[2])


    def test_delivery_requests_quantity(self):
        # self.assertGreaterEqual(len(self.cls.dr),3)
        pass

    def test_empty_drone_delivery(self):
        return True

    def test_drone_delivery(self):
        return True

        # self.assertEqual(self.dt_1_tiny.value.drone_model, DroneModel.Model_1)
        # self.assertEqual(self.dt_1_tiny.value.drone_configuration[0].package_type.value.size, 1)
        # self.assertEqual(self.dt_1_tiny.value.drone_configuration[0].quantity, 2)
        #
        # self.assertEqual(self.dt_1_tiny_medium.value.drone_model, DroneModel.Model_1)
        # self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[0].package_type.value.size, 1)
        # self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[0].quantity, 2)
        # self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[1].package_type.value.size, 4)
        # self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[1].quantity, 2)
        #
        # self.assertEqual(self.dt_2_tiny.value.drone_model, DroneModel.Model_2)
        # self.assertEqual(self.dt_2_tiny.value.drone_configuration[0].package_type.value.size, 1)
        # self.assertEqual(self.dt_2_tiny.value.drone_configuration[0].quantity, 4)
