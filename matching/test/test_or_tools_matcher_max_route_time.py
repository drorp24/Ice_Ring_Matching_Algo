import uuid
from datetime import datetime, timedelta
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import DeliveringDrones
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard
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
from matching.constraint_config import ConstraintsConfig, CapacityConstraints, TravelTimeConstraints, \
    PriorityConstraints, SessionTimeConstraints
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.monitor_config import MonitorConfig
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_matcher_constraints import MAX_OPERATION_TIME
from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.solver_config import SolverVendor

ZERO_TIME = DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00))


class ORToolsMatcherMaxRouteTimeTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # This test assumes different max route times per drone formation, with similar velocity
        cls.loading_dock = cls._create_loading_dock()
        cls.delivering_drones_1 = cls._create_limited_route_time_delivering_drones(cls.loading_dock,
                                                                                         max_route_times_in_minutes=20,
                                                                                         velocity_meter_per_sec=10.0)
        cls.delivering_drones1_max_endurance = cls.delivering_drones_1.max_route_time_in_minutes
        cls.delivering_drones1_max_range = cls.delivering_drones_1.get_formation_max_range_in_meters()
        cls.delivering_drones1_velocity_per_minute = cls.delivering_drones_1.velocity_meter_per_sec * 60.0
        cls.delivering_drones_2 = cls._create_sufficient_route_time_delivering_drones(
            loading_dock=cls.loading_dock,
            max_route_times_in_minutes=60,
            velocity_meter_per_sec=10.0)
        cls.delivering_drones2_max_endurance = cls.delivering_drones_2.max_route_time_in_minutes
        cls.delivering_drones2_max_range = cls.delivering_drones_2.get_formation_max_range_in_meters()
        cls.delivering_drones2_velocity_per_minute = cls.delivering_drones_2.velocity_meter_per_sec * 60.0
        cls.delivering_drones_board_1 = DeliveringDronesBoard([cls.delivering_drones_1])
        cls.delivering_drones_board_2 = DeliveringDronesBoard([cls.delivering_drones_2])

    def test_when_travel_time_is_greater_than_max_route_time(self):
        delivery_requests = self._create_2_delivery_requests_with_big_travel_time_difference()
        match_config = self._create_match_config_with_waiting_time(waiting_time=0)
        graph = self._create_graph(delivery_requests, self.loading_dock,
                                   1 / self.delivering_drones2_velocity_per_minute,
                                   1 / self.delivering_drones2_velocity_per_minute)  # Assuming Velocity of delivering_drones1 and delivering_drones2 is similar
        if abs(graph.calc_max_cost() - self.delivering_drones2_max_endurance / 2.0) > 1e-6:
            print('Check cost calculation')
        match_input_1 = MatcherInput(graph, self.delivering_drones_board_1, match_config)
        match_input_2 = MatcherInput(graph, self.delivering_drones_board_2, match_config)
        matcher_1 = ORToolsMatcher(match_input_1)
        matcher_2 = ORToolsMatcher(match_input_2)
        delivery_board_1 = matcher_1.match()
        delivery_board_2 = matcher_2.match()

        self.assertEqual(1, len(delivery_board_1.drone_deliveries[0].matched_requests))
        self.assertEqual(2, len(delivery_board_2.drone_deliveries[0].matched_requests))

    @staticmethod
    def _create_limited_route_time_delivering_drones(loading_dock: DroneLoadingDock, max_route_times_in_minutes: int, velocity_meter_per_sec: float):
        return DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                drone_formation=DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1),
                                start_loading_dock=loading_dock,
                                end_loading_dock=loading_dock,
                                max_route_time_in_minutes=max_route_times_in_minutes,
                                velocity_meter_per_sec=velocity_meter_per_sec)

    @staticmethod
    def _create_match_config_with_waiting_time(waiting_time: int = 0):
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(SolverVendor.OR_TOOLS, first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True, capacity_cost_coefficient=1),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=waiting_time,
                                                              max_route_time=MAX_OPERATION_TIME,
                                                              count_time_from_zero=False,
                                                              reloading_time=0),
                session_time_constraints=SessionTimeConstraints(max_session_time=MAX_OPERATION_TIME),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=100)),
            unmatched_penalty=100000,
            reload_per_vehicle=0,
            monitor=MonitorConfig(enabled=False)
        )

    def _create_2_delivery_requests_with_big_time_window_difference(self):
        dr1_range = self.delivering_drones1_max_range / 10.0
        dr2_range = self.delivering_drones2_max_range / 10.0
        delivering_drones1_travel_time_to_dr1 = dr1_range / self.delivering_drones1_velocity_per_minute
        delivering_drones2_travel_time_to_dr2 = dr2_range / self.delivering_drones2_velocity_per_minute
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, dr1_range),
                create_point_2d(0, dr2_range)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=delivering_drones1_travel_time_to_dr1)))),
                TimeWindowExtension(
                    since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=self.delivering_drones1_max_endurance))),
                    until=ZERO_TIME.add_time_delta(
                        TimeDeltaExtension(timedelta(minutes=self.delivering_drones1_max_endurance + delivering_drones2_travel_time_to_dr2)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE: 1}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

    def _create_2_delivery_requests_with_big_travel_time_difference(self):
        dr1_range = self.delivering_drones1_max_range / 10.0
        dr2_range = self.delivering_drones2_max_range / 2.0
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, dr1_range),
                create_point_2d(0, dr2_range)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(
                        TimeDeltaExtension(timedelta(minutes=self.delivering_drones1_max_endurance / 5.0)))),
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=self.delivering_drones2_max_endurance)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.TINY: 2}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

    @staticmethod
    def _create_sufficient_route_time_delivering_drones(loading_dock: DroneLoadingDock,
                                                           max_route_times_in_minutes: int,
                                                           velocity_meter_per_sec: float):
        return DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                drone_formation=DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1),
                                start_loading_dock=loading_dock,
                                end_loading_dock=loading_dock,
                                max_route_time_in_minutes=max_route_times_in_minutes,
                                velocity_meter_per_sec=velocity_meter_per_sec)

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(EntityID.generate_uuid(),DroneLoadingStation(EntityID.generate_uuid(),create_point_2d(0, 0)),
                                DroneType.drone_type_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=4)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock,
                      edge_cost_factor: float = 1.0, edge_travel_time_factor: float = 1.0) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph, edge_cost_factor, edge_travel_time_factor)
        return graph
