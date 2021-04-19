import uuid
from datetime import timedelta, date, time
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
from common.entities.base_entities.entity_distribution.priority_distribution import ExactPriorityDistribution
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
from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.solver_config import SolverVendor

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class ORToolsMatcherReloadWithDifferentPriorityTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        cls.loading_dock = cls._create_loading_dock()
        cls.graph = cls._create_graph(cls.delivery_requests, cls.loading_dock)
        cls.delivering_drones_board = cls._create_delivering_drones_board(cls.loading_dock)
        cls.match_input = MatcherInput(cls.graph, cls.delivering_drones_board, cls._create_match_config())
        matcher = ORToolsMatcher(cls.match_input)
        cls.actual_delivery_board = matcher.match()

    def test_matcher_reload_requests(self):
        self.assert_max_reload_was_done()
        self.assert_one_extra_request_dropped_with_lowest_priority()
        self.assert_highest_priority_delivered_first()
        self.assert_all_loaded_packages_delivered()

    def assert_all_loaded_packages_delivered(self):
        for delivery in self.actual_delivery_board.drone_deliveries:
            self.assertEqual(4, len(delivery.matched_requests))

    def assert_highest_priority_delivered_first(self):
        first_session_total_priority = self.actual_delivery_board.drone_deliveries[0].get_total_priority()
        second_session_total_priority = self.actual_delivery_board.drone_deliveries[1].get_total_priority()
        self.assertLess(first_session_total_priority, second_session_total_priority)

    def assert_one_extra_request_dropped_with_lowest_priority(self):
        self.assertEqual(1, len(self.actual_delivery_board.unmatched_delivery_requests))
        self.assertEqual(17, self.actual_delivery_board.unmatched_delivery_requests[0].delivery_request.priority)

    def assert_max_reload_was_done(self):
        self.assertEqual(4, len(self.actual_delivery_board.drone_deliveries))

    @staticmethod
    def _create_delivery_requests() -> List[DeliveryRequest]:
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
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
            time_window_distribution=ExactTimeWindowDistribution(17*[
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(hours=2)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE: 1}),
            priority_distribution=ExactPriorityDistribution(list(range(1, 18)))
        )
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 17})

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
    def _create_delivering_drones_board(loading_dock: DroneLoadingDock) -> DeliveringDronesBoard:
        delivering_drones_1 = DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                                  drone_formation=DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES, DroneType.drone_type_1),
                                                  start_loading_dock=loading_dock,
                                                  end_loading_dock=loading_dock)
        delivering_drones_2 = DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                                  drone_formation=DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES, DroneType.drone_type_1),
                                                  start_loading_dock=loading_dock,
                                                  end_loading_dock=loading_dock)
        return DeliveringDronesBoard([delivering_drones_1, delivering_drones_2])

    @staticmethod
    def _create_match_config() -> MatcherConfig:
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(SolverVendor.OR_TOOLS, first_solution_strategy="PATH_CHEAPEST_ARC",
                                       local_search_strategy="GUIDED_LOCAL_SEARCH", timeout_sec=10),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True, capacity_cost_coefficient=1),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=0,
                                                              max_route_time=1440,
                                                              count_time_from_zero=False,
                                                              reloading_time=30,
                                                              important_earliest_coeff=1),
                session_time_constraints=SessionTimeConstraints(max_session_time=60),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=100)),
            unmatched_penalty=10000,
            reload_per_vehicle=1,
            monitor=MonitorConfig(enabled=False)
        )
