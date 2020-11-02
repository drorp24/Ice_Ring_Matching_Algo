from common.tools.fleet_reader import FleetReader
from common.entities.drone import PlatformType
from common.entities.drone_formation import FormationSize, DroneFormations, FormationOptions
from common.tools.fleet_partition import FleetPartition
from common.tools.fleet_configuration_attribution import FleetConfigurationAttribution
import unittest
from pathlib import Path


class TestFleetConfigurationAttribution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fleet_reader = FleetReader(Path('TestFleet.json'))

    def test_fleet_configuration_with_none_zero_policy(self):
        platform_property_set = self.fleet_reader.get_platform_properties(PlatformType.platform_1)
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
                    FormationOptions.TINY_PACKAGES][FormationSize.MEDIUM][PlatformType.platform_1]], 2)

    def test_fleet_configuration_with_zero_policy(self):
        platform_property_set = self.fleet_reader.get_platform_properties(PlatformType.platform_2)
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
