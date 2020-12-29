import unittest

from common.entities.base_entities.drone import PlatformType, Configurations
from common.entities.base_entities.drone_formation import FormationSize, DroneFormations, FormationOptions
from common.tools.fleet_configuration_attribution import FleetConfigurationAttribution
from common.tools.fleet_partition import FleetPartition
from common.tools.fleet_property_sets import PlatformPropertySet, PlatformFormationsSizePolicyPropertySet, \
    PlatformConfigurationsPolicyPropertySet


class TestFleetConfigurationAttribution(unittest.TestCase):

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

    def test_fleet_configuration_with_none_zero_policy(self):
        platform_property_set = self.platform_property_set_1
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, platform_property_set)
        drone_formation_per_type_amounts = FleetConfigurationAttribution.solve()
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.LARGE_PACKAGES][FormationSize.MINI][PlatformType.platform_1]], 1)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.LARGE_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_1]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.MEDIUM_PACKAGES][FormationSize.MINI][PlatformType.platform_1]], 4)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.MEDIUM_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_1]], 1)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.MEDIUM_PACKAGES][FormationSize.MINI][PlatformType.platform_1]], 4)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.MEDIUM_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_1]], 1)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.SMALL_PACKAGES][FormationSize.MINI][PlatformType.platform_1]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.SMALL_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_1]], 2)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.TINY_PACKAGES][FormationSize.MINI][PlatformType.platform_1]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.TINY_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_1]], 1)

    def test_fleet_configuration_with_zero_policy(self):
        platform_property_set = self.platform_property_set_2
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, platform_property_set)
        drone_formation_per_type_amounts = FleetConfigurationAttribution.solve()
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.LARGE_PACKAGES][FormationSize.MINI][PlatformType.platform_2]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.LARGE_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_2]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.MEDIUM_PACKAGES][FormationSize.MINI][PlatformType.platform_2]], 6)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.MEDIUM_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_2]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.SMALL_PACKAGES][FormationSize.MINI][PlatformType.platform_2]], 9)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.SMALL_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_2]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.TINY_PACKAGES][FormationSize.MINI][PlatformType.platform_2]], 0)
        self.assertEqual(
            drone_formation_per_type_amounts.amounts[
                DroneFormations.drone_formations_map[
                    FormationOptions.TINY_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_2]], 0)
