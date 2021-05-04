import uuid
from datetime import datetime, timedelta
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import DeliveringDrones
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard
from common.entities.base_entities.drone_formation import DroneFormations, DroneFormationType, \
    PackageConfigurationOption
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import ExactTimeWindowDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.fleet_property_sets import BoardLevelProperties
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension, TimeDeltaExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from geometry.distribution.geo_distribution import ExactPointLocationDistribution
from geometry.geo_factory import create_point_2d
from matching.constraint_config import ConstraintsConfig, CapacityConstraints, TravelTimeConstraints, \
    PriorityConstraints
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.monitor_config import MonitorConfig
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_matcher_constraints import MAX_OPERATION_TIME
from matching.ortools.ortools_solver_config import ORToolsSolverConfig

ZERO_TIME = DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00))


class ORToolsMatcherMaxSessionTimeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loading_dock = cls._create_loading_dock()
        cls.default_max_session_time = 400
        cls.modified_max_session_time = 100

    def test_when_travel_time_is_lower_than_max_session_time(self):
        delivery_requests = \
            self._create_delivery_request_with_given_max_session_time(max_session_time=self.modified_max_session_time)
        delivering_drones_default_max_session_time = \
            self._create_delivering_drones_given_max_session_time(self.loading_dock, self.default_max_session_time)
        match_config = self._create_match_config_with_waiting_time(waiting_time=0)
        graph = self._create_graph(
            delivery_requests, self.loading_dock)
        match_input = MatcherInput(graph, DeliveringDronesBoard([delivering_drones_default_max_session_time]),
                                   match_config)
        matcher = ORToolsMatcher(match_input)
        delivery_board = matcher.match()
        self.assertEqual(len(delivery_board.unmatched_delivery_requests), 0)

    def test_when_travel_time_is_larger_than_max_session_time(self):
        delivery_requests = \
            self._create_delivery_request_with_given_max_session_time(
                max_session_time=self.default_max_session_time / 2)
        delivering_drones_default_max_session_time = \
            self._create_delivering_drones_given_max_session_time(self.loading_dock, self.default_max_session_time)
        match_config = self._create_match_config_with_waiting_time(waiting_time=0)
        graph = self._create_graph(
            delivery_requests, self.loading_dock)
        match_input = MatcherInput(graph, DeliveringDronesBoard([delivering_drones_default_max_session_time]),
                                   match_config)
        matcher = ORToolsMatcher(match_input)
        delivery_board = matcher.match()
        self.assertEqual(len(delivery_board.unmatched_delivery_requests), 1)

    def test_when_travel_time_both_are_larger_than_max_session_time(self):
        delivery_requests = \
            self._create_delivery_request_with_given_max_session_time(max_session_time=self.default_max_session_time)
        delivering_drones_default_max_session_time = \
            self._create_delivering_drones_given_max_session_time(self.loading_dock, self.modified_max_session_time)
        match_config = self._create_match_config_with_waiting_time(waiting_time=0)
        graph = self._create_graph(
            delivery_requests, self.loading_dock)
        match_input = MatcherInput(graph, DeliveringDronesBoard([delivering_drones_default_max_session_time]),
                                   match_config)
        matcher = ORToolsMatcher(match_input)
        delivery_board = matcher.match()
        self.assertEqual(len(delivery_board.unmatched_delivery_requests), 2)

    @staticmethod
    def _create_match_config_with_waiting_time(waiting_time: int = 0):
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True, capacity_cost_coefficient=1),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=waiting_time,
                                                              max_route_time=MAX_OPERATION_TIME,
                                                              count_time_from_zero=False,
                                                              reloading_time=0,
                                                              important_earliest_coeff=1),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=100)),
            unmatched_penalty=100000,
            reload_per_vehicle=0,
            monitor=MonitorConfig(enabled=False),
            submatch_time_window_minutes=MAX_OPERATION_TIME
        )

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(EntityID.generate_uuid(),
                                DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 0)),
                                DroneType.drone_type_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=1440)))))

    def _create_delivery_request_with_given_max_session_time(self, max_session_time: int):
        dr1_range = max_session_time
        dr2_range = 2 * max_session_time
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, dr1_range),
                create_point_2d(0, dr2_range)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(
                        TimeDeltaExtension(timedelta(minutes=max_session_time * 5.0)))),
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(
                        TimeDeltaExtension(timedelta(minutes=max_session_time * 5.0)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.TINY: 2}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

    def _create_delivering_drones_given_max_session_time(self, loading_dock: DroneLoadingDock, max_session_time: int):
        board_level_properties = BoardLevelProperties(max_route_time_entire_board=1440, velocity_entire_board=1)
        delivering_drones = DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                             drone_formation=DroneFormations.get_drone_formation(
                                                 DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES,
                                                 DroneType.drone_type_1),
                                             start_loading_dock=loading_dock,
                                             end_loading_dock=loading_dock,
                                             board_level_properties=board_level_properties)
        delivering_drones.drone_formation.drone_package_configuration.max_session_time = max_session_time
        return delivering_drones

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock,
                      edge_cost_factor: float = 1.0, edge_travel_time_factor: float = 1.0) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph, edge_cost_factor, edge_travel_time_factor)
        return graph
