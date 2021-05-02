import unittest

from common.entities.base_entities.drone import DroneType, PackageConfiguration, DroneTypeToPackageConfigurationOptions, \
    DronePackageConfiguration


class BasicDroneTypeToPackageConfigurationOptionsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.drone_type_1 = DroneType.drone_type_1
        cls.drone_type_2 = DroneType.drone_type_2
        cls.configuration_1 = PackageConfiguration.MEDIUM_X4
        cls.configuration_2 = PackageConfiguration.LARGE_X4

    def test_add_configuration_option(self):
        DroneTypeToPackageConfigurationOptions.add_configuration_option(
            {self.drone_type_1: {self.configuration_1: 100}})
        expected_drone_package_configuration = DronePackageConfiguration(drone_type=self.drone_type_1,
                                                                         package_type_map=self.configuration_1.value,
                                                                         max_session_time=100)
        self.assertEqual(
            DroneTypeToPackageConfigurationOptions.get_drone_configuration(drone_type=self.drone_type_1,
                                                                           configuration=self.configuration_1),
            expected_drone_package_configuration)

    def test_update_max_session_time(self):
        DroneTypeToPackageConfigurationOptions.update_max_session_time(drone_type=self.drone_type_1,
                                                                       configuration=self.configuration_1,
                                                                       max_session_time=300)
        self.assertEqual(DroneTypeToPackageConfigurationOptions.get_drone_configuration(drone_type=self.drone_type_1,
                                                                                        configuration=self.configuration_1).max_session_time,
                         300)
