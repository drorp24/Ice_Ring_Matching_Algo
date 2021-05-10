from common.entities.base_entities.fleet.policy_determination import PolicyConfigDeterminationParameters, fleetPolicyDeterminationAttribution
import unittest
from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard
from common.entities.base_entities.drone_formation import DroneFormationType, DroneFormations, \
    PackageConfigurationOption, DroneFormation
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.delivering_drones_board_generation import generate_delivering_drones_board
from common.entities.base_entities.fleet.fleet_configuration_attribution import FleetConfigurationAttribution
from common.entities.base_entities.fleet.fleet_partition import FleetPartition
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy, BoardLevelProperties
from common.entities.base_entities.temporal import TimeWindowExtension, TimeDeltaExtension
from common.entities.base_entities.tests.test_drone_delivery import ZERO_TIME
from geometry.geo_factory import create_point_2d
from datetime import timedelta
from common.entities.base_entities.temporal import DateTimeExtension
from matching.matcher_config import ConstraintsConfig, MatcherConfig
from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.constraint_config import CapacityConstraints, PriorityConstraints, TravelTimeConstraints
from datetime import date, time
from matching.monitor_config import MonitorConfig

class TestPolicyDetermination (unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.drone_set_properties_1 = TestPolicyDetermination.define_drone_set_properties_1()
        cls.drone_set_properties_2 = TestPolicyDetermination.define_drone_set_properties_2()

        cls.config_obj = MatcherConfig(
            zero_time=DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)),
            solver=ORToolsSolverConfig(first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True, capacity_cost_coefficient=1000),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=10,
                                                              max_route_time=1440,
                                                              count_time_from_zero=False,
                                                              reloading_time=0,
                                                              important_earliest_coeff=1),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=1000)),
            unmatched_penalty=100000,
            reload_per_vehicle=0,
            monitor=MonitorConfig(enabled=True,
                                  iterations_between_monitoring=10,
                                  max_iterations=100000,
                                  save_plot=True,
                                  show_plot=True,
                                  separate_charts=True,
                                  output_directory="outputs"),
            submatch_time_window_minutes=1440
        )

    def test_policy_determination(self):
        fleetPolicyDeterminationAttribution.extract_parameters([self.drone_set_properties_1, self.drone_set_properties_2], self.config_obj)

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
            drone_amount=20)