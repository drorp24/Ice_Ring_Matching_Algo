from common.tools.fleet_reader import FleetReader
from common.tools.fleet_property_sets  import PlatformPropertySet, PlatformFormationsSizePolicyPropertySet, \
    PlatformConfigurationsPolicyPropertySet
from common.entities.base_entities.drone import PlatformType, Configurations
from common.entities.base_entities.drone_formation import FormationSize
import unittest
from common.tools.tests.path_utils import create_path_from_current_directory, Path


class BasicFleetReaderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fleet_reader = FleetReader(create_path_from_current_directory(Path('TestFleet.json')))

    def test_platform_property_set(self):
        platform_property_set = self.fleet_reader.get_platform_properties(PlatformType.platform_1)
        self.assertIsInstance(platform_property_set, PlatformPropertySet)
        self.assertEqual(platform_property_set.platform_type, PlatformType.platform_1)
        self.assertEqual(platform_property_set.size, 30)
        self.assertIsInstance(platform_property_set.formation_policy, PlatformFormationsSizePolicyPropertySet)
        self.assertIsInstance(platform_property_set.configuration_policy, PlatformConfigurationsPolicyPropertySet)

    def test_formation_size_policy(self):
        formation_size_policy_property_set = self.fleet_reader.get_formation_size_policy(PlatformType.platform_2)
        self.assertIsInstance(formation_size_policy_property_set, PlatformFormationsSizePolicyPropertySet)
        self.assertEqual(formation_size_policy_property_set.formation_size_policy[FormationSize.MINI], 1.0)
        self.assertEqual(formation_size_policy_property_set.formation_size_policy[FormationSize.MEDIUM], 0.0)

    def test_drone_configuration_policy(self):
        platform_configuration_policy = self.fleet_reader.get_configurations_policy(PlatformType.platform_1)
        self.assertIsInstance(platform_configuration_policy, PlatformConfigurationsPolicyPropertySet)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.LARGE_X2], 0.1)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.MEDIUM_X4], 0.4)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.SMALL_X8], 0.3)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.TINY_X16], 0.2)
