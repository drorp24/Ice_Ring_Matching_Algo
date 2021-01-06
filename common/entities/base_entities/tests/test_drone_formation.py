import unittest

from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_formation import DroneFormationType, DroneFormations, PackageConfigurationOptions
from common.entities.base_entities.package import PackageType


class BasicDroneFormationTypeGenerationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._2X_PLATFORM_1_2X8 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                     PackageConfigurationOptions.LARGE_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._4X_PLATFORM_1_2X8 = DroneFormations.get_drone_formation(DroneFormationType.QUAD,
                                                                     PackageConfigurationOptions.LARGE_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._2X_PLATFORM_1_4X4 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                     PackageConfigurationOptions.MEDIUM_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._4X_PLATFORM_1_4X4 = DroneFormations.get_drone_formation(DroneFormationType.QUAD,
                                                                     PackageConfigurationOptions.MEDIUM_PACKAGES,
                                                                     DroneType.drone_type_1)
        cls._2X_PLATFORM_2_4X8 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                     PackageConfigurationOptions.LARGE_PACKAGES,
                                                                     DroneType.drone_type_2)
        cls._4X_PLATFORM_2_8X4 = DroneFormations.get_drone_formation(DroneFormationType.QUAD,
                                                                     PackageConfigurationOptions.MEDIUM_PACKAGES,
                                                                     DroneType.drone_type_2)
        cls._2X_PLATFORM_2_16X2 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                      PackageConfigurationOptions.SMALL_PACKAGES,
                                                                      DroneType.drone_type_2)
        cls._2X_PLATFORM_2_32X1 = DroneFormations.get_drone_formation(DroneFormationType.PAIR,
                                                                      PackageConfigurationOptions.TINY_PACKAGES,
                                                                      DroneType.drone_type_2)

    def test_formation_size(self):
        self.assertEqual(self._2X_PLATFORM_1_2X8.size, DroneFormationType.PAIR)
        self.assertEqual(self._4X_PLATFORM_1_2X8.size, DroneFormationType.QUAD)
        self.assertEqual(self._2X_PLATFORM_1_4X4.size, DroneFormationType.PAIR)
        self.assertEqual(self._4X_PLATFORM_1_4X4.size, DroneFormationType.QUAD)
        self.assertEqual(self._2X_PLATFORM_2_4X8.size, DroneFormationType.PAIR)
        self.assertEqual(self._4X_PLATFORM_2_8X4.size, DroneFormationType.QUAD)
        self.assertEqual(self._2X_PLATFORM_2_16X2.size, DroneFormationType.PAIR)
        self.assertEqual(self._2X_PLATFORM_2_32X1.size, DroneFormationType.PAIR)

    def test_package_type_size(self):
        self.assertEqual(self._2X_PLATFORM_1_2X8.get_package_type_volume(PackageType.LARGE), 2)
        self.assertEqual(self._4X_PLATFORM_1_2X8.get_package_type_volume(PackageType.LARGE), 2)
        self.assertEqual(self._2X_PLATFORM_1_4X4.get_package_type_volume(PackageType.MEDIUM), 4)
        self.assertEqual(self._4X_PLATFORM_1_4X4.get_package_type_volume(PackageType.MEDIUM), 4)
        self.assertEqual(self._2X_PLATFORM_2_4X8.get_package_type_volume(PackageType.LARGE), 4)
        self.assertEqual(self._4X_PLATFORM_2_8X4.get_package_type_volume(PackageType.MEDIUM), 8)
        self.assertEqual(self._2X_PLATFORM_2_16X2.get_package_type_volume(PackageType.SMALL), 16)
        self.assertEqual(self._2X_PLATFORM_2_32X1.get_package_type_volume(PackageType.TINY), 32)
