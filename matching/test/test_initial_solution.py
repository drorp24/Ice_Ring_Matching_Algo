from datetime import time, date, timedelta
from random import Random
from unittest import TestCase

from common.entities.base_entities.drone import PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.drone_loading_station_distribution import \
    DroneLoadingStationDistribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    TimeWindowDistribution, DateTimeDistribution
from common.entities.base_entities.fleet.delivering_drones_board_generation import build_delivering_drones_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneFormationTypePolicy, \
    PackageConfigurationPolicy, DroneSetProperties, BoardLevelProperties
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension
from experiment_space.distribution.supplier_category_distribution import SupplierCategoryDistribution
from experiment_space.graph_creation_algorithm import calc_assignment_from_init_solution, DeliveryRequest, \
    FullyConnectedGraphAlgorithm
from geometry.distribution.geo_distribution import NormalPointDistribution, UniformPointInBboxDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d
from matching.constraint_config import ConstraintsConfig, CapacityConstraints, TravelTimeConstraints, PriorityConstraints
from matching.matcher_config import MatcherConfig
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput
from matching.matching_master import MatchingMaster
from matching.monitor_config import MonitorConfig
from matching.ortools.ortools_initial_solution import ORToolsInitialSolution
from matching.ortools.ortools_solver_config import ORToolsSolverConfig

ZERO_TIME = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(0, 0, 0))


class BasicInitialSolutionTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category_distribution = BasicInitialSolutionTest.create_supplier_category()

    def test_initial_solution(self):
        supplier_category = self.supplier_category_distribution.choose_rand(random=Random(10),
                                                                            amount={DeliveryRequest: 50,
                                                                                    DroneLoadingDock: 1})[0]

        delivering_drones_board = BasicInitialSolutionTest.create_delivering_drones_board(
            amount=6,
            max_route_time_entire_board=1440,
            velocity_entire_board=10.0,
            loading_docks=supplier_category.drone_loading_docks
        )

        time_overlapping_dependent_graph = FullyConnectedGraphAlgorithm(edge_cost_factor=25.0,
                                                                        edge_travel_time_factor=25.0).create(
            supplier_category)
        match_config_initial = BasicInitialSolutionTest.create_match_config(local_search_strategy="GUIDED_LOCAL_SEARCH",
                                                                            reload_per_vehicle=3)
        matcher_input = MatcherInput(graph=time_overlapping_dependent_graph,
                                     delivering_drones_board=delivering_drones_board,
                                     config=match_config_initial)

        routes = ORToolsInitialSolution.calc(matcher_input=matcher_input)
        for route in routes.as_list():
            self.assertEqual(len(set(route)), len(route))

    def test_set_initial_solution(self):
        supplier_category = self.supplier_category_distribution.choose_rand(random=Random(10),
                                                                            amount={DeliveryRequest: 37,
                                                                                    DroneLoadingDock: 1})[0]
        delivering_drones_board = BasicInitialSolutionTest.create_delivering_drones_board(
            loading_docks=supplier_category.drone_loading_docks,
            amount=6,
            max_route_time_entire_board=1440,
            velocity_entire_board=10.0)

        time_overlapping_dependent_graph = FullyConnectedGraphAlgorithm(edge_cost_factor=25.0,
                                                                        edge_travel_time_factor=25.0).create(
            supplier_category)

        match_config_auto_noreuse = BasicInitialSolutionTest.create_match_config(local_search_strategy="AUTOMATIC",
                                                                                 reload_per_vehicle=0)
        matcher_input_auto_noreuse = MatcherInput(graph=time_overlapping_dependent_graph,
                                                  delivering_drones_board=delivering_drones_board,
                                                  config=match_config_auto_noreuse)

        delivery_board_auto_noreuse = MatchingMaster(matcher_input=matcher_input_auto_noreuse).match()

        match_config_initial = BasicInitialSolutionTest.create_match_config(local_search_strategy="GUIDED_LOCAL_SEARCH",
                                                                            reload_per_vehicle=3)

        matcher_input_initial_reuse = MatcherInput(graph=time_overlapping_dependent_graph,
                                                   delivering_drones_board=delivering_drones_board,
                                                   config=match_config_initial)

        initial_routes = ORToolsInitialSolution.calc(matcher_input=matcher_input_initial_reuse)

        match_config_auto_reuse = BasicInitialSolutionTest.create_match_config(local_search_strategy="AUTOMATIC",
                                                                               reload_per_vehicle=3)
        matcher_input_auto_reuse = MatcherInput(graph=time_overlapping_dependent_graph,
                                                delivering_drones_board=delivering_drones_board,
                                                config=match_config_auto_reuse)

        delivery_board_using_initial_routes = calc_assignment_from_init_solution(matcher_input=matcher_input_auto_reuse,
                                                                                 initial_routes=initial_routes)

        self.assertLessEqual(len(delivery_board_using_initial_routes.unmatched_delivery_requests),
                             len(delivery_board_auto_noreuse.unmatched_delivery_requests))
        self.assertGreaterEqual(delivery_board_using_initial_routes.get_total_priority(),
                                delivery_board_auto_noreuse.get_total_priority())

    @staticmethod
    def create_match_config(local_search_strategy: str = "automatic", reload_per_vehicle: int = 0) -> MatcherConfig:
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy=local_search_strategy, timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True,
                                                         capacity_cost_coefficient=10000),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=0,
                                                              max_route_time=1440,
                                                              count_time_from_zero=False,
                                                              reloading_time=120,
                                                              important_earliest_coeff=1),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=1000)),
            unmatched_penalty=10000,
            reload_per_vehicle=reload_per_vehicle,
            monitor=MonitorConfig(enabled=False),
            submatch_time_window_minutes=1440
        )

    @staticmethod
    def create_supplier_category() -> SupplierCategoryDistribution:
        return SupplierCategoryDistribution(
            zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
            delivery_requests_distribution=BasicInitialSolutionTest.create_delivery_request_distribution(
                create_point_2d(35.11, 32.0), 0.1,
                0.1, 10, 20),
            drone_loading_docks_distribution=DroneLoadingDockDistribution(
                drone_loading_station_distributions=DroneLoadingStationDistribution(
                    drone_station_locations_distribution=UniformPointInBboxDistribution(35.11,
                                                                                        35.11,
                                                                                        31.79, 31.79
                                                                                        )),
                time_window_distributions=BasicInitialSolutionTest.create_standard_full_day_test_time()))

    @staticmethod
    def create_single_package_distribution():
        package_type_distribution_dict = {PackageType.LARGE: 1}
        package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
        return package_distribution

    @staticmethod
    def create_delivery_request_distribution(center_point: Point2D, sigma_lon: float, sigma_lat: float,
                                             lowest_priority: int = 10, dr_timewindow: int = 3):
        package_distribution = BasicInitialSolutionTest.create_single_package_distribution()
        zero_time = ZERO_TIME
        time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=dr_timewindow, minutes=0))])
        dt_options = [zero_time.add_time_delta(TimeDeltaExtension(timedelta(hours=x))) for x in
                      range(24 - dr_timewindow)]

        time_window_distribution = TimeWindowDistribution(DateTimeDistribution(dt_options), time_delta_distrib)

        delivery_request_distribution = build_delivery_request_distribution(
            package_type_distribution=package_distribution,
            relative_dr_location_distribution=NormalPointDistribution(center_point, sigma_lon, sigma_lat),
            priority_distribution=PriorityDistribution(list(range(1, lowest_priority))),
            time_window_distribution=time_window_distribution)
        return delivery_request_distribution

    @staticmethod
    def create_standard_full_day_test_time():
        default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=23, minutes=59))])
        default_dt_options = [ZERO_TIME]
        return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)

    @staticmethod
    def create_delivering_drones_board(
            loading_docks: [DroneLoadingDock],
            drone_formation_policy=DroneFormationTypePolicy(
                {DroneFormationType.PAIR: 1, DroneFormationType.QUAD: 0}),
            package_configurations_policy=PackageConfigurationPolicy({PackageConfiguration.LARGE_X2: 1,
                                                                      PackageConfiguration.MEDIUM_X4: 0,
                                                                      PackageConfiguration.SMALL_X8: 0,
                                                                      PackageConfiguration.TINY_X16: 0}),
            amount: int = 30, max_route_time_entire_board: int = 400, velocity_entire_board: float = 10.0):
        drone_set_properties = DroneSetProperties(drone_type=loading_docks[0].drone_type,
                                                  package_configuration_policy=package_configurations_policy,
                                                  drone_formation_policy=drone_formation_policy,
                                                  drone_amount=amount,
                                                  start_loading_dock=loading_docks[0],
                                                  end_loading_dock=loading_docks[0])
        return build_delivering_drones_board(drone_set_properties, BoardLevelProperties(max_route_time_entire_board,
                                                                                        velocity_entire_board))
