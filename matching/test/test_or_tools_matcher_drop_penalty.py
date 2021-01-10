from datetime import timedelta, date, time
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PlatformType
from common.entities.base_entities.drone_delivery import DroneDelivery, MatchedDroneLoadingDock, EmptyDroneDelivery
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, EmptyDroneDeliveryBoard, \
    DroppedDeliveryRequest
from common.entities.base_entities.drone_formation import DroneFormations, FormationOptions, FormationSize
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import ExactTimeWindowDistribution
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension, TimeDeltaExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from geometry.distribution.geo_distribution import ExactPointLocationDistribution
from geometry.geo_factory import create_point_2d
from matching.matcher_config import MatcherConfig, MatcherConfigProperties, MatcherSolver, \
    MatcherConstraints, \
    CapacityConstraints, TimeConstraints, PriorityConstraints
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class ORToolsMatcherDropPenaltyTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        cls.loading_dock = cls._create_loading_dock()
        cls.graph = cls._create_graph(cls.delivery_requests, cls.loading_dock)
        cls.empty_board = cls._create_empty_board()
        cls.match_config = cls._create_match_config()
        cls.match_input = MatcherInput(cls.graph, cls.empty_board, cls.match_config)

    def test_matcher_when_drop_penalty_zero_then_no_matched_requests(self):
        matcher = ORToolsMatcher(self.match_input)
        actual_delivery_board = matcher.match()

        drone_delivery = DroneDelivery(id_=self.empty_board.empty_drone_deliveries[0].id,
                                       drone_formation=self.empty_board.empty_drone_deliveries[
                                           0].drone_formation,
                                       matched_requests=[],
                                       start_drone_loading_docks=MatchedDroneLoadingDock(
                                           graph_index=0,
                                           drone_loading_dock=self.loading_dock,
                                           delivery_min_time=ZERO_TIME,
                                           delivery_max_time=ZERO_TIME),
                                       end_drone_loading_docks=MatchedDroneLoadingDock(
                                           graph_index=0,
                                           drone_loading_dock=self.loading_dock,
                                           delivery_min_time=ZERO_TIME,
                                           delivery_max_time=ZERO_TIME))

        dropped_delivery_request = self._create_dropped(self.delivery_requests)

        expected_matched_board = DroneDeliveryBoard(drone_deliveries=[drone_delivery],
                                                    dropped_delivery_requests=dropped_delivery_request)
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
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 3})

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
                                PlatformType.platform_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=5)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest],
                      loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph)
        return graph

    @staticmethod
    def _create_empty_board() -> EmptyDroneDeliveryBoard:
        empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))

        return EmptyDroneDeliveryBoard([empty_drone_delivery_1])

    @staticmethod
    def _create_match_config() -> MatcherConfig:
        match_config_properties = MatcherConfigProperties(
            zero_time=DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)),
            first_solution_strategy="or_tools:path_cheapest_arc",
            solver=MatcherSolver(full_name="or_tools:automatic", timeout_sec=30),
            match_constraints=MatcherConstraints(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=10,
                                                 max_route_time=300,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            dropped_penalty=0)

        return MatcherConfig(match_config_properties=match_config_properties)

    @staticmethod
    def _create_dropped(delivery_requests: List[DeliveryRequest]):
        return [DroppedDeliveryRequest(graph_index=1, delivery_request=delivery_requests[0]),
                DroppedDeliveryRequest(graph_index=2, delivery_request=delivery_requests[1]),
                DroppedDeliveryRequest(graph_index=3, delivery_request=delivery_requests[2])]
