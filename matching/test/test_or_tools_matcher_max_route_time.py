import uuid
from datetime import datetime, timedelta
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PlatformType
from common.entities.base_entities.drone_delivery import EmptyDroneDelivery
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormations, FormationOptions, FormationSize
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
        # This test assumes different max route times per drone formation, with similar velocity
        cls.empty_drone_delivery_1.drone_formation.set_max_route_times_in_minutes(20)
        cls.empty_drone_delivery_1.drone_formation.set_velocity_meter_per_sec(10.0)
        cls.edd1_max_endurance = cls.empty_drone_delivery_1.drone_formation.max_route_times_in_minutes
        cls.edd1_max_range = cls.empty_drone_delivery_1.drone_formation.get_formation_max_range_in_meters()
        cls.edd1_velocity_per_minute = cls.empty_drone_delivery_1.drone_formation.velocity_meter_per_sec * 60.0
        cls.empty_drone_delivery_2 = cls._create_sufficient_route_time_empty_drone_delivery()
        cls.empty_drone_delivery_2.drone_formation.set_max_route_times_in_minutes(60)
        cls.empty_drone_delivery_2.drone_formation.set_velocity_meter_per_sec(10.0)
        cls.edd2_max_endurance = cls.empty_drone_delivery_2.drone_formation.max_route_times_in_minutes
        cls.edd2_max_range = cls.empty_drone_delivery_2.drone_formation.get_formation_max_range_in_meters()
        cls.edd2_velocity_per_minute = cls.empty_drone_delivery_2.drone_formation.velocity_meter_per_sec * 60.0
        cls.empty_board_1 = EmptyDroneDeliveryBoard([cls.empty_drone_delivery_1])
        cls.empty_board_2 = EmptyDroneDeliveryBoard([cls.empty_drone_delivery_2])

    def test_when_wait_time_longer_than_max_route_time(self):
        delivery_requests = self._create_2_delivery_requests_with_big_time_window_difference()
        match_config = self._create_match_config_with_waiting_time(waiting_time=self.edd2_max_endurance)
        graph = self._create_graph(delivery_requests, self.loading_dock, 1/self.edd2_velocity_per_minute) # Assuming Velocity of edd1 and edd2 is similar
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
        match_config = self._create_match_config_with_waiting_time(waiting_time=0)
        graph = self._create_graph(delivery_requests, self.loading_dock, 1/self.edd2_velocity_per_minute) # Assuming Velocity of edd1 and edd2 is similar
        if graph.calc_max_cost() > self.edd2_max_endurance/2.0:
            print('Check cost calculation')
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
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))

    @staticmethod
    def _create_match_config_with_waiting_time(waiting_time: int=0):
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(SolverVendor.OR_TOOLS, first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=waiting_time,
                                                 max_route_time=MAX_OPERATION_TIME,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            unmatched_penalty=1000)

    def _create_2_delivery_requests_with_big_time_window_difference(self):
        dr1_range = self.edd1_max_range / 10.0
        dr2_range = self.edd2_max_range / 10.0
        edd1_travel_time_to_dr1 = dr1_range / self.edd1_velocity_per_minute
        edd2_travel_time_to_dr2 = dr2_range / self.edd2_velocity_per_minute
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, dr1_range),
                create_point_2d(0, dr2_range)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=edd1_travel_time_to_dr1)))),
                TimeWindowExtension(
                    since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=self.edd1_max_endurance))),
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=self.edd1_max_endurance+edd2_travel_time_to_dr2)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

    def _create_2_delivery_requests_with_big_travel_time_difference(self):
        dr1_range = self.edd1_max_range / 10.0
        dr2_range = self.edd2_max_range / 2.0
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, dr1_range),
                create_point_2d(0, dr2_range)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=self.edd1_max_endurance/5.0)))),
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=self.edd2_max_endurance)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

    @staticmethod
    def _create_sufficient_route_time_empty_drone_delivery():
        return EmptyDroneDelivery(EntityID(uuid.uuid4()), DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_2))

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
                                PlatformType.platform_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=4)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock, factor: float=1.0) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph, factor)
        return graph
