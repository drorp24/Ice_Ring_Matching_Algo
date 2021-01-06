import unittest

from common.entities.base_entities.drone import DroneType, PackageConfigurations
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormationType, DroneFormations, \
    PackageConfigurationOptions, DroneFormation
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_configuration_attribution import FleetConfigurationAttribution
from common.entities.base_entities.fleet.fleet_partition import FleetPartition
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationPolicy, \
    PackageConfigurationsPolicy


class TestFleetConfigurationAttribution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.drone_set_properties_1 = TestFleetConfigurationAttribution.define_drone_set_properties_1()
        cls.drone_set_properties_2 = TestFleetConfigurationAttribution.define_drone_set_properties_2()
        cls.formation_size_policy = DroneFormationPolicy({DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0})

    def test_fleet_configuration_with_none_zero_policy(self):
        drone_set_properties = self.drone_set_properties_1
        FleetPartition.extract_parameters(drone_set_properties)
        fleet_formation_amounts = FleetPartition.solve()
        FleetConfigurationAttribution.extract_parameters(fleet_formation_amounts, drone_set_properties)
        fleet_configuration = FleetConfigurationAttribution.solve()

        expected_outcome = {
            (DroneType.drone_platform_1, DroneFormationType.PAIR, PackageConfigurationOptions.LARGE_PACKAGES): 1,
            (DroneType.drone_platform_1, DroneFormationType.QUAD, PackageConfigurationOptions.LARGE_PACKAGES): 0,
            (DroneType.drone_platform_1, DroneFormationType.PAIR, PackageConfigurationOptions.MEDIUM_PACKAGES): 4,
            (DroneType.drone_platform_1, DroneFormationType.QUAD, PackageConfigurationOptions.MEDIUM_PACKAGES): 1,
            (DroneType.drone_platform_1, DroneFormationType.PAIR, PackageConfigurationOptions.SMALL_PACKAGES): 0,
            (DroneType.drone_platform_1, DroneFormationType.QUAD, PackageConfigurationOptions.SMALL_PACKAGES): 2,
            (DroneType.drone_platform_1, DroneFormationType.PAIR, PackageConfigurationOptions.TINY_PACKAGES): 0,
            (DroneType.drone_platform_1, DroneFormationType.QUAD, PackageConfigurationOptions.TINY_PACKAGES): 1
        }

        self._assert_fleet_configuration_is_correct(expected_outcome, fleet_configuration)

    def test_fleet_configuration_with_zero_policy(self):
        platform_property_set = self.drone_set_properties_2
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, platform_property_set)
        fleet_configuration = FleetConfigurationAttribution.solve()

        expected_outcome = {
            (DroneType.drone_platform_2, DroneFormationType.PAIR, PackageConfigurationOptions.LARGE_PACKAGES): 0,
            (DroneType.drone_platform_2, DroneFormationType.QUAD, PackageConfigurationOptions.LARGE_PACKAGES): 0,
            (DroneType.drone_platform_2, DroneFormationType.PAIR, PackageConfigurationOptions.MEDIUM_PACKAGES): 6,
            (DroneType.drone_platform_2, DroneFormationType.QUAD, PackageConfigurationOptions.MEDIUM_PACKAGES): 0,
            (DroneType.drone_platform_2, DroneFormationType.PAIR, PackageConfigurationOptions.SMALL_PACKAGES): 9,
            (DroneType.drone_platform_2, DroneFormationType.QUAD, PackageConfigurationOptions.SMALL_PACKAGES): 0,
            (DroneType.drone_platform_2, DroneFormationType.PAIR, PackageConfigurationOptions.TINY_PACKAGES): 0,
            (DroneType.drone_platform_2, DroneFormationType.QUAD, PackageConfigurationOptions.TINY_PACKAGES): 0
        }

        self._assert_fleet_configuration_is_correct(expected_outcome, fleet_configuration)

    def test_none_zero_formation_policy(self):
        platform_property_set = self.drone_set_properties_1
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.PAIR], 5)
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.QUAD], 5)

    def test_with_zero_formation_policy(self):
        platform_property_set = self.drone_set_properties_2
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.PAIR], 15)
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.QUAD], 0)

    def test_empty_drone_delivery_board(self):
        empty_drone_delivery_board = generate_empty_delivery_board(
            [self.drone_set_properties_1, self.drone_set_properties_2])
        self.assertIsInstance(empty_drone_delivery_board, EmptyDroneDeliveryBoard)
        self.assertEqual(len(empty_drone_delivery_board.empty_drone_deliveries), 24)
        self.assertIsInstance(empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation, DroneFormation)

    @classmethod
    def define_drone_set_properties_1(cls):
        return DroneSetProperties(
            drone_type=DroneType.drone_platform_1,
            drone_platform_formation_policy=DroneFormationPolicy(
                {DroneFormationType.PAIR: 0.5,
                 DroneFormationType.QUAD: 0.5}),
            package_configuration_policy=PackageConfigurationsPolicy(
                {PackageConfigurations.LARGE_X2: 0.1,
                 PackageConfigurations.MEDIUM_X4: 0.4,
                 PackageConfigurations.SMALL_X8: 0.3,
                 PackageConfigurations.TINY_X16: 0.2}),
            drone_amount=30)

    @classmethod
    def define_drone_set_properties_2(cls):
        return DroneSetProperties(
            drone_type=DroneType.drone_platform_2,
            drone_platform_formation_policy=DroneFormationPolicy(
                {DroneFormationType.PAIR: 1.0,
                 DroneFormationType.QUAD: 0.0}),
            package_configuration_policy=PackageConfigurationsPolicy(
                {PackageConfigurations.LARGE_X4: 0.0,
                 PackageConfigurations.MEDIUM_X8: 0.4,
                 PackageConfigurations.SMALL_X16: 0.6,
                 PackageConfigurations.TINY_X32: 0.0}),
            drone_amount=30)

    def _assert_fleet_configuration_is_correct(self, expected_outcome, fleet_configuration):
        for fleet_option, expected_amount in expected_outcome.items():
            self._assertCorrectFleetConfigurationAmount(fleet_configuration_amounts=fleet_configuration,
                                                        drone_type=fleet_option[0],
                                                        formation_type=fleet_option[1],
                                                        package_configuration=fleet_option[2],
                                                        expected_amount=expected_amount)

    def _assertCorrectFleetConfigurationAmount(self, fleet_configuration_amounts, drone_type, formation_type,
                                               package_configuration,
                                               expected_amount):
        self.assertEqual(
            fleet_configuration_amounts.amounts[
                DroneFormations.drone_formations_map[package_configuration][formation_type][drone_type]],
            expected_amount)
