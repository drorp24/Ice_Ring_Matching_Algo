import unittest

from common.entities.base_entities.drone import PlatformType, Configurations
from common.entities.base_entities.drone_formation import FormationSize
from common.tools.fleet_property_sets import PlatformPropertySet, PlatformFormationsSizePolicyPropertySet, \
    PlatformConfigurationsPolicyPropertySet


class BasicFleetReaderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.platform_property_set = PlatformPropertySet(
            platform_type=PlatformType.platform_1,
            formation_policy=PlatformFormationsSizePolicyPropertySet(
                {FormationSize.MINI: 0.5,
                 FormationSize.MEDIUM: 0.5}),
            configuration_policy=PlatformConfigurationsPolicyPropertySet(
                {Configurations.LARGE_X2: 0.1,
                 Configurations.MEDIUM_X4: 0.4,
                 Configurations.SMALL_X8: 0.3,
                 Configurations.TINY_X16: 0.2}),
            size=30)

        cls.formation_size_policy_property_set = PlatformFormationsSizePolicyPropertySet(
            {FormationSize.MINI: 1.0, FormationSize.MEDIUM: 0.0})

    def test_platform_property_set(self):
        self.assertIsInstance(self.platform_property_set, PlatformPropertySet)
        self.assertEqual(self.platform_property_set.platform_type, PlatformType.platform_1)
        self.assertEqual(self.platform_property_set.size, 30)
        self.assertIsInstance(self.platform_property_set.formation_policy, PlatformFormationsSizePolicyPropertySet)
        self.assertIsInstance(self.platform_property_set.configuration_policy, PlatformConfigurationsPolicyPropertySet)

    def test_formation_size_policy(self):
        self.assertIsInstance(self.formation_size_policy_property_set, PlatformFormationsSizePolicyPropertySet)
        self.assertEqual(self.formation_size_policy_property_set.formation_size_policy[FormationSize.MINI], 1.0)
        self.assertEqual(self.formation_size_policy_property_set.formation_size_policy[FormationSize.MEDIUM], 0.0)

    def test_drone_configuration_policy(self):
        platform_configuration_policy = self.platform_property_set.configuration_policy
        self.assertIsInstance(platform_configuration_policy, PlatformConfigurationsPolicyPropertySet)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.LARGE_X2], 0.1)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.MEDIUM_X4], 0.4)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.SMALL_X8], 0.3)
        self.assertEqual(platform_configuration_policy.configurations_policy[Configurations.TINY_X16], 0.2)
