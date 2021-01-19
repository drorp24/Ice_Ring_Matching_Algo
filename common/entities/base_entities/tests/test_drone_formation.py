import unittest

from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_formation import DroneFormationType, DroneFormations, PackageConfigurationOption
from common.entities.base_entities.package import PackageType


class BasicDroneFormationTypeGenerationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._2X_drone_type_1_2X8 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                     PackageConfigurationOption.LARGE_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._4X_drone_type_1_2X8 = DroneFormations.get_drone_formation(DroneFormationType.QUAD,
                                                                     PackageConfigurationOption.LARGE_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._2X_drone_type_1_4X4 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                     PackageConfigurationOption.MEDIUM_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._4X_drone_type_1_4X4 = DroneFormations.get_drone_formation(DroneFormationType.QUAD,
                                                                     PackageConfigurationOption.MEDIUM_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._2X_drone_type_2_4X8 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                     PackageConfigurationOption.LARGE_PACKAGES,
                                                                     DroneType.drone_type_2)
        cls._4X_drone_type_2_8X4 = DroneFormations.get_drone_formation(DroneFormationType.QUAD,
                                                                     PackageConfigurationOption.MEDIUM_PACKAGES,
                                                                     DroneType.drone_type_2)
        cls._2X_drone_type_2_16X2 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                      PackageConfigurationOption.SMALL_PACKAGES,
                                                                      DroneType.drone_type_2)
        cls._2X_drone_type_2_32X1 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                      PackageConfigurationOption.TINY_PACKAGES,
                                                                      DroneType.drone_type_2)

    def test_formation_size(self):
        self.assertEqual(self._2X_drone_type_1_2X8.drone_formation_type, DroneFormationType.PAIR)
        self.assertEqual(self._4X_drone_type_1_2X8.drone_formation_type, DroneFormationType.QUAD)
        self.assertEqual(self._2X_drone_type_1_4X4.drone_formation_type, DroneFormationType.PAIR)
        self.assertEqual(self._4X_drone_type_1_4X4.drone_formation_type, DroneFormationType.QUAD)
        self.assertEqual(self._2X_drone_type_2_4X8.drone_formation_type, DroneFormationType.PAIR)
        self.assertEqual(self._4X_drone_type_2_8X4.drone_formation_type, DroneFormationType.QUAD)
        self.assertEqual(self._2X_drone_type_2_16X2.drone_formation_type, DroneFormationType.PAIR)
        self.assertEqual(self._2X_drone_type_2_32X1.drone_formation_type, DroneFormationType.PAIR)

    def test_package_type_size(self):
        self.assertEqual(self._2X_drone_type_1_2X8.get_package_type_amount(PackageType.LARGE), 4)
        self.assertEqual(self._4X_drone_type_1_2X8.get_package_type_amount(PackageType.LARGE), 8)
        self.assertEqual(self._2X_drone_type_1_4X4.get_package_type_amount(PackageType.MEDIUM), 8)
        self.assertEqual(self._4X_drone_type_1_4X4.get_package_type_amount(PackageType.MEDIUM), 16)
        self.assertEqual(self._2X_drone_type_2_4X8.get_package_type_amount(PackageType.LARGE), 8)
        self.assertEqual(self._4X_drone_type_2_8X4.get_package_type_amount(PackageType.MEDIUM), 32)
        self.assertEqual(self._2X_drone_type_2_16X2.get_package_type_amount(PackageType.SMALL), 32)
        self.assertEqual(self._2X_drone_type_2_32X1.get_package_type_amount(PackageType.TINY), 64)
