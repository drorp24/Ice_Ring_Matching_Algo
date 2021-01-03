import unittest

from common.entities.base_entities.drone import PlatformType, Configurations
from common.entities.base_entities.drone_formation import FormationSize
from common.entities.base_entities.fleet.fleet_partition import FleetPartition
from common.entities.base_entities.fleet.fleet_property_sets import PlatformPropertySet, PlatformFormationsSizePolicyPropertySet, \
    PlatformConfigurationsPolicyPropertySet


class FleetPartitionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.platform_property_set_1 = PlatformPropertySet(
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

        cls.platform_property_set_2 = PlatformPropertySet(
            platform_type=PlatformType.platform_2,
            formation_policy=PlatformFormationsSizePolicyPropertySet(
                {FormationSize.MINI: 1.0,
                 FormationSize.MEDIUM: 0.0}),
            configuration_policy=PlatformConfigurationsPolicyPropertySet(
                {Configurations.LARGE_X4: 0.0,
                 Configurations.MEDIUM_X8: 0.4,
                 Configurations.SMALL_X16: 0.6,
                 Configurations.TINY_X32: 0.0}),
            size=30)

        cls.formation_size_policy_property_set = PlatformFormationsSizePolicyPropertySet(
            {FormationSize.MINI: 1.0, FormationSize.MEDIUM: 0.0})

    def test_none_zero_formation_policy(self):
        platform_property_set = self.platform_property_set_1
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MINI], 5)
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MEDIUM], 5)

    def test_with_zero_formation_policy(self):
        platform_property_set = self.platform_property_set_2
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MINI], 15)
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MEDIUM], 0)
