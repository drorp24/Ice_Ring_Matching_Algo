import uuid
from datetime import timedelta, date, time
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import EmptyDroneDelivery, DroneDelivery, MatchedDeliveryRequest, \
    MatchedDroneLoadingDock
from common.entities.base_entities.drone_delivery_board import UnmatchedDeliveryRequest, DroneDeliveryBoard, \
    EmptyDroneDeliveryBoard
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
from matching.constraint_config import ConstraintsConfig, CapacityConstraints, TimeConstraints, PriorityConstraints
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.monitor_config import MonitorConfig
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.solver_config import SolverVendor

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class ORToolsMatcherDifferentPriorityTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        cls.loading_dock = cls._create_loading_dock()
        cls.graph = cls._create_graph(cls.delivery_requests, cls.loading_dock)
        cls.empty_board = cls._create_empty_board()
        cls.match_input = MatcherInput(cls.graph, cls.empty_board, cls._create_match_config())

    def test_matcher_when_requests_with_different_priorities(self):
        matcher = ORToolsMatcher(self.match_input)
        actual_delivery_board = matcher.match()

        expected_drone_deliveries = self._create_drone_deliveries(delivery_requests=self.delivery_requests,
                                                                  empty_board=self.empty_board,
                                                                  loading_dock=self.loading_dock)
        unmatched_delivery_request = UnmatchedDeliveryRequest(graph_index=2, delivery_request=self.delivery_requests[1])
        expected_matched_board = DroneDeliveryBoard(
            drone_deliveries=expected_drone_deliveries,
            unmatched_delivery_requests=[unmatched_delivery_request])

        self.assertEqual(expected_matched_board, actual_delivery_board)

    @staticmethod
    def _create_delivery_requests() -> List[DeliveryRequest]:
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
                create_point_2d(0, 10),
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
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}),
            priority_distribution=ExactPriorityDistribution([1, 10, 1])
        )
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 3})

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(EntityID.generate_uuid(),DroneLoadingStation(EntityID.generate_uuid(),create_point_2d(0, 0)),
                                DroneType.drone_type_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=1)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph)
        return graph

    @staticmethod
    def _create_empty_board() -> EmptyDroneDeliveryBoard:
        empty_drone_delivery_1 = EmptyDroneDelivery(EntityID(uuid.uuid4()), DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.LARGE_PACKAGES, DroneType.drone_type_1))
        return EmptyDroneDeliveryBoard([empty_drone_delivery_1])

    @staticmethod
    def _create_match_config() -> MatcherConfig:
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(SolverVendor.OR_TOOLS, first_solution_strategy="path_cheapest_arc",
                                       local_search_strategy="automatic", timeout_sec=30),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=10,
                                                 max_route_time=300,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            unmatched_penalty=5,
            monitor=MonitorConfig(enabled=False))

    @staticmethod
    def _create_drone_deliveries(delivery_requests: List[DeliveryRequest], empty_board: EmptyDroneDeliveryBoard,
                                 loading_dock: DroneLoadingDock) -> List[DroneDelivery]:
        drone_delivery_1 = DroneDelivery(id_=empty_board.empty_drone_deliveries[0].id,
                                         drone_formation=empty_board.empty_drone_deliveries[0].drone_formation,
                                         matched_requests=[MatchedDeliveryRequest(
                                             graph_index=3,
                                             delivery_request=delivery_requests[2],
                                             matched_delivery_option_index=0,
                                             delivery_time_window=TimeWindowExtension(
                                                 since=ZERO_TIME.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=15))),
                                                 until=ZERO_TIME.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=15))))),
                                             MatchedDeliveryRequest(
                                                 graph_index=1,
                                                 delivery_request=delivery_requests[0],
                                                 matched_delivery_option_index=0,
                                                 delivery_time_window=TimeWindowExtension(
                                                     since=ZERO_TIME.add_time_delta(
                                                         TimeDeltaExtension(timedelta(minutes=25))),
                                                     until=ZERO_TIME.add_time_delta(
                                                         TimeDeltaExtension(timedelta(minutes=25))))),
                                         ],
                                         start_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=0,
                                             drone_loading_dock=loading_dock,
                                             delivery_time_window=TimeWindowExtension(
                                                 since=loading_dock.time_window.since,
                                                 until=loading_dock.time_window.since)),
                                         end_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=0,
                                             drone_loading_dock=loading_dock,
                                             delivery_time_window=TimeWindowExtension(
                                                 since=loading_dock.time_window.since.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=30))),
                                                 until=loading_dock.time_window.since.add_time_delta(
                                                     TimeDeltaExtension(timedelta(minutes=30)))))
                                         )
        return [drone_delivery_1]
