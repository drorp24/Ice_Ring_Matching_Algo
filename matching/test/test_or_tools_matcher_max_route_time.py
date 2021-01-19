import uuid
from datetime import datetime, timedelta
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import EmptyDroneDelivery
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormations, PackageConfigurationOption, \
    DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import ExactTimeWindowDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeWindowExtension, DateTimeExtension, TimeDeltaExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from geometry.distribution.geo_distribution import ExactPointLocationDistribution
from geometry.geo_factory import create_point_2d
from matching.constraint_config import ConstraintsConfig, CapacityConstraints, TimeConstraints, PriorityConstraints
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_matcher_constraints import MAX_OPERATION_TIME
from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.solver_config import SolverVendor

ZERO_TIME = DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00))


class ORToolsMatcherMaxRouteTimeTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loading_dock = cls._create_loading_dock()
        cls.empty_drone_delivery_1 = cls._create_limited_route_time_empty_drone_delivery()
        cls.empty_drone_delivery_2 = cls._create_sufficient_route_time_empty_drone_delivery()
        cls.empty_board_1 = EmptyDroneDeliveryBoard([cls.empty_drone_delivery_1])
        cls.empty_board_2 = EmptyDroneDeliveryBoard([cls.empty_drone_delivery_2])

    def test_when_wait_time_longer_than_max_route_time(self):
        delivery_requests = self._create_2_delivery_requests_with_big_time_window_difference()
        match_config = self._create_match_config_with_big_waiting_time()
        graph = self._create_graph(delivery_requests, self.loading_dock)
        match_input_1 = MatcherInput(graph, self.empty_board_1, match_config)
        match_input_2 = MatcherInput(graph, self.empty_board_2, match_config)
        matcher_1 = ORToolsMatcher(match_input_1)
        matcher_2 = ORToolsMatcher(match_input_2)
        delivery_board_1 = matcher_1.match()
        delivery_board_2 = matcher_2.match()

        self.assertEqual(1, len(delivery_board_1.drone_deliveries[0].matched_requests))
        self.assertEqual(2, len(delivery_board_2.drone_deliveries[0].matched_requests))

    def test_when_travel_time_is_greater_than_max_route_time(self):
        delivery_requests = self._create_2_delivery_requests_with_big_travel_time_difference()
        match_config = self._create_match_config_with_zero_waiting_time()
        graph = self._create_graph(delivery_requests, self.loading_dock)
        match_input_1 = MatcherInput(graph, self.empty_board_1, match_config)
        match_input_2 = MatcherInput(graph, self.empty_board_2, match_config)
        matcher_1 = ORToolsMatcher(match_input_1)
        matcher_2 = ORToolsMatcher(match_input_2)
        delivery_board_1 = matcher_1.match()
        delivery_board_2 = matcher_2.match()

        self.assertEqual(1, len(delivery_board_1.drone_deliveries[0].matched_requests))
        self.assertEqual(2, len(delivery_board_2.drone_deliveries[0].matched_requests))

    @staticmethod
    def _create_limited_route_time_empty_drone_delivery():
        return EmptyDroneDelivery(EntityID(uuid.uuid4()), DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES, DroneType.drone_type_1))

    @staticmethod
    def _create_match_config_with_big_waiting_time():
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(SolverVendor.OR_TOOLS, first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=500,
                                                 max_route_time=MAX_OPERATION_TIME,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            unmatched_penalty=1000)

    @staticmethod
    def _create_2_delivery_requests_with_big_time_window_difference():
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
                create_point_2d(0, 10)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=5)))),
                TimeWindowExtension(
                    since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=400))),
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=500)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

    @staticmethod
    def _create_match_config_with_zero_waiting_time():
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(SolverVendor.OR_TOOLS, first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=0,
                                                 max_route_time=MAX_OPERATION_TIME,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            unmatched_penalty=1000)

    @staticmethod
    def _create_2_delivery_requests_with_big_travel_time_difference():
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
                create_point_2d(0, 300)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=15)))),
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=400)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

    @staticmethod
    def _create_sufficient_route_time_empty_drone_delivery():
        return EmptyDroneDelivery(EntityID(uuid.uuid4()), DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES, DroneType.drone_type_2))

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
                                DroneType.drone_type_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=4)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph)
        return graph
