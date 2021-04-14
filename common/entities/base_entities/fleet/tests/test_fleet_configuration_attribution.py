import unittest
from datetime import timedelta
from pathlib import Path

from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard
from common.entities.base_entities.drone_formation import DroneFormationType, DroneFormations, \
    PackageConfigurationOption, DroneFormation
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_configuration_attribution import FleetConfigurationAttribution
from common.entities.base_entities.fleet.fleet_partition import FleetPartition
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy
from common.entities.base_entities.temporal import TimeWindowExtension, TimeDeltaExtension
from common.entities.base_entities.tests.test_drone_delivery import ZERO_TIME
from geometry.geo_factory import create_point_2d


class TestFleetConfigurationAttribution(unittest.TestCase):
    empty_drone_delivery_board_json_path = Path('common/entities/base_entities/fleet/tests/empty_drone_test_file.json')

    @classmethod
    def setUpClass(cls):
        cls.drone_set_properties_1 = TestFleetConfigurationAttribution.define_drone_set_properties_1()
        cls.drone_set_properties_2 = TestFleetConfigurationAttribution.define_drone_set_properties_2()
        cls.formation_size_policy = DroneFormationTypePolicy({DroneFormationType.PAIR: 1.0,
                                                              DroneFormationType.QUAD: 0.0})

    @classmethod
    def tearDownClass(cls):
        cls.empty_drone_delivery_board_json_path.unlink()

    def test_fleet_configuration_with_none_zero_policy(self):
        drone_set_properties = self.drone_set_properties_1
        fleet_formation_amounts = FleetPartition(drone_set_properties).solve()
        FleetConfigurationAttribution.extract_parameters(fleet_formation_amounts, drone_set_properties)
        fleet_configuration = FleetConfigurationAttribution.solve()

        expected_outcome = {
            (DroneType.drone_type_1, DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES): 1,
            (DroneType.drone_type_1, DroneFormationType.QUAD, PackageConfigurationOption.LARGE_PACKAGES): 0,
            (DroneType.drone_type_1, DroneFormationType.PAIR, PackageConfigurationOption.MEDIUM_PACKAGES): 4,
            (DroneType.drone_type_1, DroneFormationType.QUAD, PackageConfigurationOption.MEDIUM_PACKAGES): 1,
            (DroneType.drone_type_1, DroneFormationType.PAIR, PackageConfigurationOption.SMALL_PACKAGES): 0,
            (DroneType.drone_type_1, DroneFormationType.QUAD, PackageConfigurationOption.SMALL_PACKAGES): 2,
            (DroneType.drone_type_1, DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES): 0,
            (DroneType.drone_type_1, DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES): 1
        }

        self._assert_fleet_configuration_is_correct(expected_outcome, fleet_configuration)

    def test_fleet_configuration_with_zero_policy(self):
        drone_set_properties = self.drone_set_properties_2
        formation_sizes_amounts = FleetPartition(drone_set_properties).solve()
        FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, drone_set_properties)
        fleet_configuration = FleetConfigurationAttribution.solve()

        expected_outcome = {
            (DroneType.drone_type_2, DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES): 0,
            (DroneType.drone_type_2, DroneFormationType.QUAD, PackageConfigurationOption.LARGE_PACKAGES): 0,
            (DroneType.drone_type_2, DroneFormationType.PAIR, PackageConfigurationOption.MEDIUM_PACKAGES): 6,
            (DroneType.drone_type_2, DroneFormationType.QUAD, PackageConfigurationOption.MEDIUM_PACKAGES): 0,
            (DroneType.drone_type_2, DroneFormationType.PAIR, PackageConfigurationOption.SMALL_PACKAGES): 9,
            (DroneType.drone_type_2, DroneFormationType.QUAD, PackageConfigurationOption.SMALL_PACKAGES): 0,
            (DroneType.drone_type_2, DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES): 0,
            (DroneType.drone_type_2, DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES): 0
        }

        self._assert_fleet_configuration_is_correct(expected_outcome, fleet_configuration)

    def test_none_zero_formation_policy(self):
        drone_set_properties = self.drone_set_properties_1
        formation_sizes_amounts = FleetPartition(drone_set_properties).solve()
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.PAIR], 5)
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.QUAD], 5)

    def test_with_zero_formation_policy(self):
        drone_set_properties = self.drone_set_properties_2
        formation_sizes_amounts = FleetPartition(drone_set_properties).solve()
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.PAIR], 15)
        self.assertEqual(formation_sizes_amounts.amounts[DroneFormationType.QUAD], 0)

    def test_empty_drone_delivery_board(self):
        empty_drone_delivery_board = generate_empty_delivery_board(
            [self.drone_set_properties_1, self.drone_set_properties_2], 400, 10)
        self.assertIsInstance(empty_drone_delivery_board, DeliveringDronesBoard)
        self.assertEqual(len(empty_drone_delivery_board.empty_drone_deliveries), 24)
        self.assertIsInstance(empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation, DroneFormation)

    def test_empty_board_to_json_and_back_to_empty_board(self):
        empty_drone_delivery_board = generate_empty_delivery_board(
            [self.drone_set_properties_1, self.drone_set_properties_2], 400, 10)
        empty_drone_delivery_board.to_json(self.empty_drone_delivery_board_json_path)

        empty_drone_delivery_board_from_json = \
            DeliveringDronesBoard.from_json(DeliveringDronesBoard, self.empty_drone_delivery_board_json_path)

        self.assertEqual(empty_drone_delivery_board, empty_drone_delivery_board_from_json)

    @classmethod
    def define_drone_set_properties_1(cls):
        loading_dock_1 = DroneLoadingDock(EntityID.generate_uuid(),
                                          DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 0)),
                                          DroneType.drone_type_1,
                                          TimeWindowExtension(
                                              since=ZERO_TIME,
                                              until=ZERO_TIME.add_time_delta(
                                                  TimeDeltaExtension(timedelta(hours=5)))))
        return DroneSetProperties(
            drone_type=loading_dock_1.drone_type,
            drone_formation_policy=DroneFormationTypePolicy(
                {DroneFormationType.PAIR: 0.5,
                 DroneFormationType.QUAD: 0.5}),
            package_configuration_policy=PackageConfigurationPolicy(
                {PackageConfiguration.LARGE_X2: 0.1,
                 PackageConfiguration.MEDIUM_X4: 0.4,
                 PackageConfiguration.SMALL_X8: 0.3,
                 PackageConfiguration.TINY_X16: 0.2}),
            start_loading_dock=loading_dock_1,
            end_loading_dock=loading_dock_1,
            drone_amount=30)

    @classmethod
    def define_drone_set_properties_2(cls):
        loading_dock_2 = DroneLoadingDock(EntityID.generate_uuid(),
                                          DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 0)),
                                          DroneType.drone_type_2,
                                          TimeWindowExtension(
                                              since=ZERO_TIME,
                                              until=ZERO_TIME.add_time_delta(
                                                  TimeDeltaExtension(timedelta(hours=5)))))
        return DroneSetProperties(
            drone_type=loading_dock_2.drone_type,
            drone_formation_policy=DroneFormationTypePolicy(
                {DroneFormationType.PAIR: 1.0,
                 DroneFormationType.QUAD: 0.0}),
            package_configuration_policy=PackageConfigurationPolicy(
                {PackageConfiguration.LARGE_X4: 0.0,
                 PackageConfiguration.MEDIUM_X8: 0.4,
                 PackageConfiguration.SMALL_X16: 0.6,
                 PackageConfiguration.TINY_X32: 0.0}),
            start_loading_dock=loading_dock_2,
            end_loading_dock=loading_dock_2,
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
