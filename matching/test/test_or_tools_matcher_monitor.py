import unittest
import uuid
from datetime import timedelta, date, time
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import DeliveringDrones, DroneDelivery, MatchedDeliveryRequest, \
    MatchedDroneLoadingDock
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, DeliveringDronesBoard, \
    UnmatchedDeliveryRequest
from common.entities.base_entities.drone_formation import DroneFormations, PackageConfigurationOption, \
    DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import ExactPriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import ExactTimeWindowDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeWindowExtension, TimeDeltaExtension, DateTimeExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from geometry.distribution.geo_distribution import ExactPointLocationDistribution
from geometry.geo_factory import create_point_2d
from matching.constraint_config import ConstraintsConfig, PriorityConstraints, CapacityConstraints, \
    SessionTimeConstraints, TravelTimeConstraints
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.monitor import MonitorData
from matching.monitor_config import MonitorConfig
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.solver_config import SolverVendor

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class ORToolsMatcherMonitorTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.delivery_requests_without_reloading = cls._create_delivery_requests_without_reloading()
        cls.delivery_requests_with_reloading = cls._create_delivery_requests(11)
        cls.loading_dock = cls._create_loading_dock()
        cls.graph_without_reloading = cls._create_graph(cls.delivery_requests_without_reloading, cls.loading_dock)
        cls.graph_with_reloading = cls._create_graph(cls.delivery_requests_with_reloading, cls.loading_dock)
        cls.delivering_drones_board_without_reloading = cls._create_delivering_drones_board_without_reloading(
            cls.loading_dock)
        cls.delivering_drones_board_with_reloading = cls._create_delivering_drones_board_with_reloading(
            cls.loading_dock)
        expected_drone_deliveries = cls._create_drone_deliveries(
            delivery_requests=cls.delivery_requests_without_reloading,
            delivering_drones_board=cls.delivering_drones_board_without_reloading,
            loading_dock=cls.loading_dock)
        unmatched_delivery_request = UnmatchedDeliveryRequest(graph_index=2,
                                                              delivery_request=cls.delivery_requests_without_reloading[
                                                                  1])
        cls.expected_matched_board = DroneDeliveryBoard(
            drone_deliveries=expected_drone_deliveries,
            unmatched_delivery_requests=[unmatched_delivery_request])

    def test_matcher_with_monitor(self):
        num_of_iterations = 100
        config = self._create_match_config_without_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_without_reloading, self.delivering_drones_board_without_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        self.assertEqual(self.expected_matched_board, actual_delivery_board)
        self.assertEqual(matcher.matcher_monitor.monitor.num_of_iterations, num_of_iterations)
        self.assertGreater(matcher.matcher_monitor.monitor.best_objective_value, 0)

    def test_matcher_with_monitor_without_iterations_limit(self):
        num_of_iterations = -1
        config = self._create_match_config_without_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_without_reloading, self.delivering_drones_board_without_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        self.assertEqual(self.expected_matched_board, actual_delivery_board)
        self.assertGreater(matcher.matcher_monitor.monitor.num_of_iterations, 0)
        self.assertGreater(matcher.matcher_monitor.monitor.best_objective_value, 0)

    def test_matcher_with_monitor_total_priority(self):
        num_of_iterations = -1
        config = self._create_match_config_without_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_without_reloading, self.delivering_drones_board_without_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        self.assertEqual(self.expected_matched_board, actual_delivery_board)
        self.assertGreater(len(matcher.matcher_monitor.monitor.data.values), 0)

        expected_total_priority = self._get_total_priority(config, self.expected_matched_board)

        last_stored_total_priority = matcher.matcher_monitor.monitor.data[MonitorData.total_priority.name].values[-1]

        self.assertEqual(expected_total_priority, last_stored_total_priority)

    def test_matcher_with_monitor_unmatched_delivery_requests(self):
        num_of_iterations = -1
        config = self._create_match_config_without_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_without_reloading, self.delivering_drones_board_without_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        self.assertEqual(self.expected_matched_board, actual_delivery_board)
        self.assertGreater(len(matcher.matcher_monitor.monitor.data.values), 0)

        expected_unmatched_delivery_requests = len(self.expected_matched_board.unmatched_delivery_requests)

        last_stored_unmatched_delivery_requests = \
            matcher.matcher_monitor.monitor.data[MonitorData.total_unmatched_delivery_requests.name].values[-1]

        self.assertEqual(expected_unmatched_delivery_requests, last_stored_unmatched_delivery_requests)

    def test_matcher_with_monitor_unmatched_delivery_requests_total_priority(self):
        num_of_iterations = -1
        config = self._create_match_config_without_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_without_reloading, self.delivering_drones_board_without_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        self.assertEqual(self.expected_matched_board, actual_delivery_board)
        self.assertGreater(len(matcher.matcher_monitor.monitor.data.values), 0)

        expected_unmatched_delivery_requests_total_priority = self._get_unmatched_delivery_requests_total_priority(
            config, self.expected_matched_board)

        last_stored_unmatched_delivery_requests_total_priority = \
            matcher.matcher_monitor.monitor.data[MonitorData.unmatched_delivery_requests_total_priority.name].values[-1]

        self.assertEqual(expected_unmatched_delivery_requests_total_priority,
                         last_stored_unmatched_delivery_requests_total_priority)

    def test_matcher_with_monitor_objective_value(self):
        num_of_iterations = -1
        config = self._create_match_config_without_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_without_reloading, self.delivering_drones_board_without_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        self.assertEqual(self.expected_matched_board, actual_delivery_board)
        self.assertGreater(len(matcher.matcher_monitor.monitor.data.values), 0)

        expected_total_priority = self._get_total_priority(config, self.expected_matched_board)
        expected_unmatched_delivery_requests = len(self.expected_matched_board.unmatched_delivery_requests)

        expected_minimize_delivery_time_of_high_priority = \
            self._get_minimize_delivery_time_of_high_priority(config,
                                                              self.expected_matched_board,
                                                              self.delivery_requests_without_reloading)

        expected_objective = expected_unmatched_delivery_requests * config.unmatched_penalty + \
            expected_total_priority + expected_minimize_delivery_time_of_high_priority

        last_stored_objective = matcher.matcher_monitor.monitor.data[MonitorData.objective.name].values[-1]

        self.assertEqual(expected_objective, last_stored_objective)

    def test_matcher_with_monitor_total_priority_with_reloading(self):
        num_of_iterations = -1
        config = self._create_match_config_with_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_with_reloading, self.delivering_drones_board_with_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        expected_total_priority = self._get_total_priority(config, actual_delivery_board)

        last_stored_total_priority = matcher.matcher_monitor.monitor.data[MonitorData.total_priority.name].values[-1]

        self.assertEqual(expected_total_priority, last_stored_total_priority)

    def test_matcher_with_monitor_unmatched_delivery_requests_with_reloading(self):
        num_of_iterations = -1
        config = self._create_match_config_with_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_with_reloading, self.delivering_drones_board_with_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        expected_unmatched_delivery_requests = len(actual_delivery_board.unmatched_delivery_requests)

        last_stored_unmatched_delivery_requests = \
            matcher.matcher_monitor.monitor.data[MonitorData.total_unmatched_delivery_requests.name].values[-1]

        self.assertEqual(expected_unmatched_delivery_requests, last_stored_unmatched_delivery_requests)

    def test_matcher_with_monitor_unmatched_delivery_requests_total_priority_with_reloading(self):
        num_of_iterations = -1
        config = self._create_match_config_with_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_with_reloading, self.delivering_drones_board_with_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        expected_unmatched_delivery_requests_total_priority = self._get_unmatched_delivery_requests_total_priority(
            config, actual_delivery_board)

        last_stored_unmatched_delivery_requests_total_priority = \
            matcher.matcher_monitor.monitor.data[MonitorData.unmatched_delivery_requests_total_priority.name].values[-1]

        self.assertEqual(expected_unmatched_delivery_requests_total_priority,
                         last_stored_unmatched_delivery_requests_total_priority)

    @unittest.skip  #TODO: Need to be fixed - BUG 27682
    def test_matcher_with_monitor_objective_value_with_reloading(self):
        num_of_iterations = -1
        config = self._create_match_config_with_reloading(enabled=True, max_iterations=num_of_iterations)
        match_input = MatcherInput(self.graph_with_reloading, self.delivering_drones_board_with_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        self.assertGreater(len(matcher.matcher_monitor.monitor.data.values), 0)

        total_priority = self._get_total_priority(config, actual_delivery_board)
        unmatched_delivery_requests = len(actual_delivery_board.unmatched_delivery_requests)

        minimize_delivery_time_of_high_priority = \
            self._get_minimize_delivery_time_of_high_priority(config,
                                                              actual_delivery_board,
                                                              self.delivery_requests_with_reloading)

        returns_not_empty = config.constraints.capacity.capacity_cost_coefficient * \
            self._get_num_of_packages_on_return(actual_delivery_board, 4)
        expected_objective = unmatched_delivery_requests * config.unmatched_penalty + \
            total_priority + minimize_delivery_time_of_high_priority + returns_not_empty

        last_stored_objective = matcher.matcher_monitor.monitor.data[MonitorData.objective.name].values[-1]

        self.assertEqual(expected_objective, last_stored_objective)

    @staticmethod
    def _get_minimize_delivery_time_of_high_priority(config, board, delivery_requests):
        expected_minimize_delivery_time_of_high_priority = 0
        max_priority = max([dr.priority for dr in delivery_requests])
        for drone_delivery in board.drone_deliveries:
            for matched_request in drone_delivery.matched_requests:
                coefficient = int(max_priority / (matched_request.delivery_request.priority + 1))
                expected_minimize_delivery_time_of_high_priority += coefficient * \
                    matched_request.delivery_time_window.since.get_time_delta(
                                                                        config.zero_time).in_minutes()
        return expected_minimize_delivery_time_of_high_priority

    @staticmethod
    def _get_num_of_packages_on_return(board, max_num_of_packages):
        return sum(
            [max_num_of_packages - len(drone_delivery.matched_requests) for drone_delivery in board.drone_deliveries])

    def test_matcher_without_monitor(self):
        config = self._create_match_config_without_reloading(enabled=False, max_iterations=0)
        match_input = MatcherInput(self.graph_without_reloading, self.delivering_drones_board_without_reloading, config)
        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()
        self.assertEqual(self.expected_matched_board, actual_delivery_board)

    @staticmethod
    def _create_delivery_requests_without_reloading() -> List[DeliveryRequest]:
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
                create_point_2d(0, -10),
                create_point_2d(0, 15)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=30)))),
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=30)))),
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=30)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE: 1}),
            priority_distribution=ExactPriorityDistribution([1, 10, 1])
        )
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 3})

    @staticmethod
    def _create_delivery_requests(num_of_deliveries: int) -> List[DeliveryRequest]:
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
                create_point_2d(0, 5),
                create_point_2d(0, 10),
                create_point_2d(0, 10),
                create_point_2d(0, 15),
                create_point_2d(0, 15),
                create_point_2d(0, 20),
                create_point_2d(0, 20),
                create_point_2d(0, -5),
                create_point_2d(0, -5),
                create_point_2d(0, -10),
                create_point_2d(0, -10),
                create_point_2d(0, -15),
                create_point_2d(0, -15),
                create_point_2d(0, -20),
                create_point_2d(0, -20),
            ]),
            time_window_distribution=ExactTimeWindowDistribution(num_of_deliveries * [
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(hours=2)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE: 1}),
            priority_distribution=ExactPriorityDistribution(list(range(1, num_of_deliveries + 1)))
        )
        return dist.choose_rand(Random(42), amount={DeliveryRequest: num_of_deliveries})

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(EntityID.generate_uuid(),
                                DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 0)),
                                DroneType.drone_type_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=5)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph)
        return graph

    @staticmethod
    def _create_delivering_drones_board_without_reloading(loading_dock: DroneLoadingDock) -> DeliveringDronesBoard:
        delivering_drones_1 = DeliveringDrones(
            id_=EntityID(uuid.uuid4()),
            drone_formation=DroneFormations.get_drone_formation(
                DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES, DroneType.drone_type_1),
            start_loading_dock=loading_dock,
            end_loading_dock=loading_dock)
        return DeliveringDronesBoard([delivering_drones_1])

    @staticmethod
    def _create_delivering_drones_board_with_reloading(loading_dock: DroneLoadingDock) -> DeliveringDronesBoard:
        delivering_drones_1 = DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                               drone_formation=DroneFormations.get_drone_formation(
                                                   DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES,
                                                   DroneType.drone_type_1),
                                               start_loading_dock=loading_dock,
                                               end_loading_dock=loading_dock)
        delivering_drones_2 = DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                               drone_formation=DroneFormations.get_drone_formation(
                                                   DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES,
                                                   DroneType.drone_type_1),
                                               start_loading_dock=loading_dock,
                                               end_loading_dock=loading_dock)
        return DeliveringDronesBoard([delivering_drones_1, delivering_drones_2])

    @staticmethod
    def _create_match_config_without_reloading(enabled: bool, max_iterations: int,
                                               iterations_between_monitoring: int = 1) -> MatcherConfig:
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True, capacity_cost_coefficient=1),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=0,
                                                              max_route_time=30,
                                                              count_time_from_zero=False,
                                                              reloading_time=0,
                                                              important_earliest_coeff=1),
                session_time_constraints=SessionTimeConstraints(max_session_time=30),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=100)),
            unmatched_penalty=10000,
            reload_per_vehicle=0,
            monitor=MonitorConfig(enabled=enabled, iterations_between_monitoring=iterations_between_monitoring,
                                  max_iterations=max_iterations,
                                  save_plot=False, show_plot=False, output_directory=''),
            submatch_time_window_minutes=30
        )

    @staticmethod
    def _create_match_config_with_reloading(enabled: bool, max_iterations: int,
                                            iterations_between_monitoring: int = 1) -> MatcherConfig:
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(first_solution_strategy="PATH_CHEAPEST_ARC",
                                       local_search_strategy="GUIDED_LOCAL_SEARCH", timeout_sec=10),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True, capacity_cost_coefficient=5),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=0,
                                                              max_route_time=1440,
                                                              count_time_from_zero=False,
                                                              reloading_time=30,
                                                              important_earliest_coeff=1),
                session_time_constraints=SessionTimeConstraints(max_session_time=60),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=100)),
            unmatched_penalty=10000,
            reload_per_vehicle=1,
            monitor=MonitorConfig(enabled=enabled, iterations_between_monitoring=iterations_between_monitoring,
                                  max_iterations=max_iterations,
                                  save_plot=False, show_plot=False, output_directory=''),
            submatch_time_window_minutes=1440
        )

    @staticmethod
    def _create_drone_deliveries(delivery_requests: List[DeliveryRequest],
                                 delivering_drones_board: DeliveringDronesBoard,
                                 loading_dock: DroneLoadingDock) -> List[DroneDelivery]:
        drone_delivery_1 = DroneDelivery(delivering_drones=delivering_drones_board.delivering_drones_list[0],
                                         matched_requests=[MatchedDeliveryRequest(
                                             graph_index=1,
                                             delivery_request=delivery_requests[0],
                                             matched_delivery_option_index=0,
                                             delivery_time_window=TimeWindowExtension(
                                                 since=ZERO_TIME.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=5))),
                                                 until=ZERO_TIME.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=5))))),
                                             MatchedDeliveryRequest(
                                                 graph_index=3,
                                                 delivery_request=delivery_requests[2],
                                                 matched_delivery_option_index=0,
                                                 delivery_time_window=TimeWindowExtension(
                                                     since=ZERO_TIME.add_time_delta(
                                                         TimeDeltaExtension(timedelta(minutes=15))),
                                                     until=ZERO_TIME.add_time_delta(
                                                         TimeDeltaExtension(timedelta(minutes=15))))),
                                         ],
                                         start_drone_loading_dock=MatchedDroneLoadingDock(
                                             drone_loading_dock=loading_dock,
                                             delivery_time_window=TimeWindowExtension(
                                                 since=loading_dock.time_window.since,
                                                 until=loading_dock.time_window.since)),
                                         end_drone_loading_dock=MatchedDroneLoadingDock(
                                             drone_loading_dock=loading_dock,
                                             delivery_time_window=TimeWindowExtension(
                                                 since=loading_dock.time_window.since.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=30))),
                                                 until=loading_dock.time_window.since.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=30)))))
                                         )
        return [drone_delivery_1]

    @staticmethod
    def _get_unmatched_delivery_requests_total_priority(config, board):
        return config.constraints.priority.priority_cost_coefficient * \
               sum([unmatched_delivery_request.delivery_request.priority for unmatched_delivery_request in
                    board.unmatched_delivery_requests])

    @staticmethod
    def _get_total_priority(config, board):
        return board.get_total_priority() * \
               config.constraints.priority.priority_cost_coefficient
