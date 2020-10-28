import unittest

from common.entities.drone import DroneConfigurationType, PlatformType
from common.entities.drone_formation import DroneFormationType, FormationSize
from common.entities.package import PackageType


class BasicDroneConfigurationTypeGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.PLATFORM_1_2X8 = DroneConfigurationType.PLATFORM_1_2X8
        cls.PLATFORM_1_4X4 = DroneConfigurationType.PLATFORM_1_4X4
        cls.PLATFORM_1_8X2 = DroneConfigurationType.PLATFORM_1_8X2
        cls.PLATFORM_1_16X1 = DroneConfigurationType.PLATFORM_1_16X1
        cls.PLATFORM_2_4X8 = DroneConfigurationType.PLATFORM_2_4X8
        cls.PLATFORM_2_8X4 = DroneConfigurationType.PLATFORM_2_8X4
        cls.PLATFORM_2_16X2 = DroneConfigurationType.PLATFORM_2_16X2
        cls.PLATFORM_2_32X1 = DroneConfigurationType.PLATFORM_2_32X1

    def test_platform_type(self):
        self.assertEqual(self.PLATFORM_1_2X8.value.get_platform_type().name, PlatformType.PLATFORM_1.name)
        self.assertEqual(self.PLATFORM_1_4X4.value.get_platform_type().name, PlatformType.PLATFORM_1.name)
        self.assertEqual(self.PLATFORM_1_8X2.value.get_platform_type().name, PlatformType.PLATFORM_1.name)
        self.assertEqual(self.PLATFORM_1_16X1.value.get_platform_type().name, PlatformType.PLATFORM_1.name)
        self.assertEqual(self.PLATFORM_2_4X8.value.get_platform_type().name, PlatformType.PLATFORM_2.name)
        self.assertEqual(self.PLATFORM_2_8X4.value.get_platform_type().name, PlatformType.PLATFORM_2.name)
        self.assertEqual(self.PLATFORM_2_16X2.value.get_platform_type().name, PlatformType.PLATFORM_2.name)
        self.assertEqual(self.PLATFORM_2_32X1.value.get_platform_type().name, PlatformType.PLATFORM_2.name)

    def test_package_type_volume(self):
        self.assertEqual(self.PLATFORM_1_2X8.value.get_package_type_volume(PackageType.LARGE), 2)
        self.assertEqual(self.PLATFORM_1_4X4.value.get_package_type_volume(PackageType.MEDIUM), 4)
        self.assertEqual(self.PLATFORM_1_8X2.value.get_package_type_volume(PackageType.SMALL), 8)
        self.assertEqual(self.PLATFORM_1_16X1.value.get_package_type_volume(PackageType.TINY), 16)
        self.assertEqual(self.PLATFORM_2_4X8.value.get_package_type_volume(PackageType.LARGE), 4)
        self.assertEqual(self.PLATFORM_2_8X4.value.get_package_type_volume(PackageType.MEDIUM), 8)
        self.assertEqual(self.PLATFORM_2_16X2.value.get_package_type_volume(PackageType.SMALL), 16)
        self.assertEqual(self.PLATFORM_2_32X1.value.get_package_type_volume(PackageType.TINY), 32)


class BasicDroneFormationTypeGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._2X_PLATFORM_1_2X8 = DroneFormationType._2X_PLATFORM_1_2X8
        cls._4X_PLATFORM_1_2X8 = DroneFormationType._4X_PLATFORM_1_2X8
        cls._2X_PLATFORM_1_4X4 = DroneFormationType._2X_PLATFORM_1_4X4
        cls._4X_PLATFORM_1_4X4 = DroneFormationType._4X_PLATFORM_1_4X4
        cls._2X_PLATFORM_1_8X2 = DroneFormationType._2X_PLATFORM_1_8X2
        cls._4X_PLATFORM_1_8X2 = DroneFormationType._4X_PLATFORM_1_8X2
        cls._2X_PLATFORM_1_16X1 = DroneFormationType._2X_PLATFORM_1_16X1
        cls._4X_PLATFORM_1_16X1 = DroneFormationType._4X_PLATFORM_1_16X1
        cls._2X_PLATFORM_2_4X8 = DroneFormationType._2X_PLATFORM_2_4X8
        cls._4X_PLATFORM_2_4X8 = DroneFormationType._4X_PLATFORM_2_4X8
        cls._2X_PLATFORM_2_8X4 = DroneFormationType._2X_PLATFORM_2_8X4
        cls._4X_PLATFORM_2_8X4 = DroneFormationType._4X_PLATFORM_2_8X4
        cls._2X_PLATFORM_2_16X2 = DroneFormationType._2X_PLATFORM_2_16X2
        cls._4X_PLATFORM_2_16X2 = DroneFormationType._4X_PLATFORM_2_16X2
        cls._2X_PLATFORM_2_32X1 = DroneFormationType._2X_PLATFORM_2_32X1
        cls._4X_PLATFORM_2_32X1 = DroneFormationType._4X_PLATFORM_2_32X1

    def test_formation_size(self):
        self.assertEqual(self._2X_PLATFORM_1_2X8.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_1_2X8.value.get_drone_formation_size(), FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_1_4X4.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_1_4X4.value.get_drone_formation_size(), FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_1_8X2.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_1_8X2.value.get_drone_formation_size(), FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_1_16X1.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_1_16X1.value.get_drone_formation_size(), FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_2_4X8.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_2_4X8.value.get_drone_formation_size(), FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_2_8X4.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_2_8X4.value.get_drone_formation_size(), FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_2_16X2.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_2_16X2.value.get_drone_formation_size(), FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_2_32X1.value.get_drone_formation_size(), FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_2_32X1.value.get_drone_formation_size(), FormationSize.MEDIUM)





