import unittest

from common.entities.base_entities.drone import PlatformType, Configurations, DroneConfigurations
from common.entities.base_entities.package import PackageType


class BasicDroneConfigurationTypeGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.PLATFORM_1_2X8 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_1, Configurations.LARGE_X2)
        cls.PLATFORM_1_4X4 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_1, Configurations.MEDIUM_X4)
        cls.PLATFORM_1_8X2 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_1, Configurations.SMALL_X8)
        cls.PLATFORM_1_16X1 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_1, Configurations.TINY_X16)
        cls.PLATFORM_2_4X8 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_2, Configurations.LARGE_X4)
        cls.PLATFORM_2_8X4 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_2, Configurations.MEDIUM_X8)
        cls.PLATFORM_2_16X2 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_2, Configurations.SMALL_X16)
        cls.PLATFORM_2_32X1 = DroneConfigurations.get_drone_configuration(
            PlatformType.platform_2, Configurations.TINY_X32)

    def test_platform_type(self):
        self.assertEqual(self.PLATFORM_1_2X8.platform_type, PlatformType.platform_1)
        self.assertEqual(self.PLATFORM_1_4X4.platform_type, PlatformType.platform_1)
        self.assertEqual(self.PLATFORM_1_8X2.platform_type, PlatformType.platform_1)
        self.assertEqual(self.PLATFORM_1_16X1.platform_type, PlatformType.platform_1)
        self.assertEqual(self.PLATFORM_2_4X8.platform_type, PlatformType.platform_2)
        self.assertEqual(self.PLATFORM_2_8X4.platform_type, PlatformType.platform_2)
        self.assertEqual(self.PLATFORM_2_16X2.platform_type, PlatformType.platform_2)
        self.assertEqual(self.PLATFORM_2_32X1.platform_type, PlatformType.platform_2)

    def test_package_type_volume(self):
        self.assertEqual(self.PLATFORM_1_2X8.get_package_type_volume(PackageType.LARGE), 2)
        self.assertEqual(self.PLATFORM_1_4X4.get_package_type_volume(PackageType.MEDIUM), 4)
        self.assertEqual(self.PLATFORM_1_8X2.get_package_type_volume(PackageType.SMALL), 8)
        self.assertEqual(self.PLATFORM_1_16X1.get_package_type_volume(PackageType.TINY), 16)
        self.assertEqual(self.PLATFORM_2_4X8.get_package_type_volume(PackageType.LARGE), 4)
        self.assertEqual(self.PLATFORM_2_8X4.get_package_type_volume(PackageType.MEDIUM), 8)
        self.assertEqual(self.PLATFORM_2_16X2.get_package_type_volume(PackageType.SMALL), 16)
        self.assertEqual(self.PLATFORM_2_32X1.get_package_type_volume(PackageType.TINY), 32)
