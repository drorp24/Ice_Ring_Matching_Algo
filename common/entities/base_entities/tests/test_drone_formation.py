import unittest

from common.entities.base_entities.drone import PlatformType
from common.entities.base_entities.drone_formation import FormationSize, DroneFormations, FormationOptions
from common.entities.base_entities.package import PackageType


class BasicDroneFormationTypeGenerationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._2X_PLATFORM_1_2X8 = DroneFormations.get_drone_formation(FormationSize.MINI,
                                                                     FormationOptions.LARGE_PACKAGES,
                                                                     PlatformType.platform_1)
        cls._4X_PLATFORM_1_2X8 = DroneFormations.get_drone_formation(FormationSize.MEDIUM,
                                                                     FormationOptions.LARGE_PACKAGES,
                                                                     PlatformType.platform_1)
        cls._2X_PLATFORM_1_4X4 = DroneFormations.get_drone_formation(FormationSize.MINI,
                                                                     FormationOptions.MEDIUM_PACKAGES,
                                                                     PlatformType.platform_1)
        cls._4X_PLATFORM_1_4X4 = DroneFormations.get_drone_formation(FormationSize.MEDIUM,
                                                                     FormationOptions.MEDIUM_PACKAGES,
                                                                     PlatformType.platform_1)
        cls._2X_PLATFORM_2_4X8 = DroneFormations.get_drone_formation(FormationSize.MINI,
                                                                     FormationOptions.LARGE_PACKAGES,
                                                                     PlatformType.platform_2)
        cls._4X_PLATFORM_2_8X4 = DroneFormations.get_drone_formation(FormationSize.MEDIUM,
                                                                     FormationOptions.MEDIUM_PACKAGES,
                                                                     PlatformType.platform_2)
        cls._2X_PLATFORM_2_16X2 = DroneFormations.get_drone_formation(FormationSize.MINI,
                                                                      FormationOptions.SMALL_PACKAGES,
                                                                      PlatformType.platform_2)
        cls._2X_PLATFORM_2_32X1 = DroneFormations.get_drone_formation(FormationSize.MINI,
                                                                      FormationOptions.TINY_PACKAGES,
                                                                      PlatformType.platform_2)

    def test_formation_size(self):
        self.assertEqual(self._2X_PLATFORM_1_2X8.size, FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_1_2X8.size, FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_1_4X4.size, FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_1_4X4.size, FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_2_4X8.size, FormationSize.MINI)
        self.assertEqual(self._4X_PLATFORM_2_8X4.size, FormationSize.MEDIUM)
        self.assertEqual(self._2X_PLATFORM_2_16X2.size, FormationSize.MINI)
        self.assertEqual(self._2X_PLATFORM_2_32X1.size, FormationSize.MINI)

    def test_package_type_size(self):
        self.assertEqual(self._2X_PLATFORM_1_2X8.get_package_type_volume(PackageType.LARGE), 2)
        self.assertEqual(self._4X_PLATFORM_1_2X8.get_package_type_volume(PackageType.LARGE), 2)
        self.assertEqual(self._2X_PLATFORM_1_4X4.get_package_type_volume(PackageType.MEDIUM), 4)
        self.assertEqual(self._4X_PLATFORM_1_4X4.get_package_type_volume(PackageType.MEDIUM), 4)
        self.assertEqual(self._2X_PLATFORM_2_4X8.get_package_type_volume(PackageType.LARGE), 4)
        self.assertEqual(self._4X_PLATFORM_2_8X4.get_package_type_volume(PackageType.MEDIUM), 8)
        self.assertEqual(self._2X_PLATFORM_2_16X2.get_package_type_volume(PackageType.SMALL), 16)
        self.assertEqual(self._2X_PLATFORM_2_32X1.get_package_type_volume(PackageType.TINY), 32)
