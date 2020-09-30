import unittest

from common.entities.drone import DroneType
from common.entities.drone_model import DroneModel


class BasicDroneGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dt_1_tiny = DroneType.DT_1_TINY
        cls.dt_1_tiny_medium = DroneType.DT_1_TINY_MEDIUM
        cls.dt_2_tiny = DroneType.DT_2_TINY

    def test_package_type(self):
        self.assertEqual(self.dt_1_tiny.value.drone_model, DroneModel.Model_1)
        self.assertEqual(self.dt_1_tiny.value.drone_configuration[0].package_type.value.size, 1)
        self.assertEqual(self.dt_1_tiny.value.drone_configuration[0].quantity, 2)

        self.assertEqual(self.dt_1_tiny_medium.value.drone_model, DroneModel.Model_1)
        self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[0].package_type.value.size, 1)
        self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[0].quantity, 2)
        self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[1].package_type.value.size, 4)
        self.assertEqual(self.dt_1_tiny_medium.value.drone_configuration[1].quantity, 2)

        self.assertEqual(self.dt_2_tiny.value.drone_model, DroneModel.Model_2)
        self.assertEqual(self.dt_2_tiny.value.drone_configuration[0].package_type.value.size, 1)
        self.assertEqual(self.dt_2_tiny.value.drone_configuration[0].quantity, 4)
