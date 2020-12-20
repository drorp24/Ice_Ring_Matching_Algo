from datetime import datetime, timedelta, date, time
from typing import List
from unittest import TestCase
from uuid import UUID

from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.drone import PlatformType
from common.entities.drone_delivery import EmptyDroneDelivery, DroneDelivery, MatchedDeliveryRequest, \
    MatchedDroneLoadingDock
from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard, DroppedDeliveryRequest
from common.entities.drone_formation import FormationSize, FormationOptions, DroneFormations
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.drone_loading_station import DroneLoadingStation
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.temporal import TimeWindowExtension, DateTimeExtension, TimeDeltaExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from matching.matcher_config import MatcherConfig, MatcherConfigProperties, MatcherSolver, \
    MatcherConstraints, \
    CapacityConstraints, TimeConstraints, PriorityConstraints
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class ORToolsMatcherDifferentLoadingDockIndexTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        cls.loading_dock = cls._create_loading_dock()

        cls.empty_board = cls._create_empty_board()
        cls.match_config = cls._create_match_config()

    def test_matcher_dock_start(self):
        graph_dock_start = self._create_graph_dock_start(self.delivery_requests, self.loading_dock)
        match_input = self._create_match_input(graph_dock_start, self.empty_board, self.match_config)

        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        expected_drone_deliveries = self._create_drone_deliveries_dock_start(
            delivery_requests=self.delivery_requests,
            empty_board=self.empty_board,
            loading_dock=self.loading_dock)

        expected_matched_board = DroneDeliveryBoard(
            drone_deliveries=[expected_drone_deliveries[0], expected_drone_deliveries[1]],
            dropped_delivery_requests=[])

        self.assertEqual(expected_matched_board, actual_delivery_board)

    def test_matcher_dock_end(self):
        graph_dock_end = self._create_graph_dock_end(self.delivery_requests, self.loading_dock)
        match_input = self._create_match_input(graph_dock_end, self.empty_board, self.match_config)

        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        expected_drone_deliveries = self._create_drone_deliveries_dock_end(
            delivery_requests=self.delivery_requests,
            empty_board=self.empty_board,
            loading_dock=self.loading_dock)

        expected_matched_board = DroneDeliveryBoard(
            drone_deliveries=[expected_drone_deliveries[0], expected_drone_deliveries[1]],
            dropped_delivery_requests=[])

        self.assertEqual(expected_matched_board, actual_delivery_board)

    def test_matcher_dock_middle(self):
        graph_dock_middle = self._create_graph_dock_middle(self.delivery_requests, self.loading_dock)
        match_input = self._create_match_input(graph_dock_middle, self.empty_board, self.match_config)

        matcher = ORToolsMatcher(match_input)
        actual_delivery_board = matcher.match()

        expected_drone_deliveries = self._create_drone_deliveries_dock_middle(
            delivery_requests=self.delivery_requests,
            empty_board=self.empty_board,
            loading_dock=self.loading_dock)

        expected_matched_board = DroneDeliveryBoard(
            drone_deliveries=[expected_drone_deliveries[0], expected_drone_deliveries[1]],
            dropped_delivery_requests=[])

        self.assertEqual(expected_matched_board, actual_delivery_board)

    @staticmethod
    def _create_delivery_requests() -> List[DeliveryRequest]:
        delivery_request_1 = DeliveryRequest(
            delivery_options=[DeliveryOption([CustomerDelivery([
                PackageDeliveryPlan(UUID(int=1),
                                    create_point_2d(0, 5),
                                    Angle(45, AngleUnit.DEGREE),
                                    Angle(45, AngleUnit.DEGREE),
                                    PackageType.LARGE)])])],
            time_window=TimeWindowExtension(
                since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 50, 00))),
            priority=1)

        delivery_request_2 = DeliveryRequest(
            delivery_options=[DeliveryOption([CustomerDelivery([
                PackageDeliveryPlan(UUID(int=2),
                                    create_point_2d(0, 10),
                                    Angle(45, AngleUnit.DEGREE),
                                    Angle(45, AngleUnit.DEGREE),
                                    PackageType.LARGE)])])],
            time_window=TimeWindowExtension(
                since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00)),
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 20, 00))),
            priority=1)

        delivery_request_3 = DeliveryRequest(
            delivery_options=[DeliveryOption([CustomerDelivery([
                PackageDeliveryPlan(UUID(int=3),
                                    create_point_2d(0, 15),
                                    Angle(45, AngleUnit.DEGREE),
                                    Angle(45, AngleUnit.DEGREE),
                                    PackageType.LARGE)])])],
            time_window=TimeWindowExtension(
                since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 13, 30, 00)),
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 13, 40, 00))),
            priority=1)

        return [delivery_request_1, delivery_request_2, delivery_request_3]

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
                                PlatformType.platform_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=5)))))

    @staticmethod
    def _create_graph_dock_start(delivery_requests: List[DeliveryRequest],
                                 loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph(zero_time=ZERO_TIME.get_internal())
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph)
        return graph

    @staticmethod
    def _create_graph_dock_end(delivery_requests: List[DeliveryRequest],
                               loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph(zero_time=ZERO_TIME.get_internal())
        graph.add_delivery_requests(delivery_requests)
        graph.add_drone_loading_docks([loading_dock])
        build_fully_connected_graph(graph)
        return graph

    @staticmethod
    def _create_graph_dock_middle(delivery_requests: List[DeliveryRequest],
                                  loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph(zero_time=ZERO_TIME.get_internal())
        graph.add_delivery_requests([delivery_requests[0]])
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests([delivery_requests[1], delivery_requests[2]])

        build_fully_connected_graph(graph)
        return graph

    @staticmethod
    def _create_empty_board() -> EmptyDroneDeliveryBoard:
        empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))

        empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))

        return EmptyDroneDeliveryBoard([empty_drone_delivery_1, empty_drone_delivery_2])

    @staticmethod
    def _create_match_config() -> MatcherConfig:
        match_config_properties = MatcherConfigProperties(
            zero_time=ZERO_TIME,
            first_solution_strategy="or_tools:path_cheapest_arc",
            solver=MatcherSolver(full_name="or_tools:automatic", timeout_sec=30),
            match_constraints=MatcherConstraints(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=300,
                                                 max_route_time=300,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            dropped_penalty=10)

        return MatcherConfig(match_config_properties=match_config_properties)

    @staticmethod
    def _create_match_input(graph: OperationalGraph, empty_board: EmptyDroneDeliveryBoard,
                            match_config_properties: MatcherConfig) -> MatcherInput:
        return MatcherInput(graph, empty_board, match_config_properties)

    @staticmethod
    def _create_drone_deliveries_dock_start(delivery_requests: List[DeliveryRequest],
                                            empty_board: EmptyDroneDeliveryBoard,
                                            loading_dock: DroneLoadingDock) -> List[DroneDelivery]:
        drone_delivery_1 = DroneDelivery(id_=empty_board.empty_drone_deliveries[0].id,
                                         drone_formation=empty_board.empty_drone_deliveries[0].drone_formation,
                                         matched_requests=[
                                             MatchedDeliveryRequest(
                                                 graph_index=1,
                                                 delivery_request=delivery_requests[0],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 35, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 50, 00))),
                                             MatchedDeliveryRequest(
                                                 graph_index=2,
                                                 delivery_request=delivery_requests[1],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 12, 00, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 12, 00, 00)))
                                         ],
                                         start_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=0,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=0))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=0)))),
                                         end_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=0,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=40))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=40)))))

        drone_delivery_2 = DroneDelivery(id_=empty_board.empty_drone_deliveries[1].id,
                                         drone_formation=empty_board.empty_drone_deliveries[1].drone_formation,
                                         matched_requests=[
                                             MatchedDeliveryRequest(
                                                 graph_index=3,
                                                 delivery_request=delivery_requests[2],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 13, 30, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 13, 30, 00)))
                                         ],
                                         start_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=0,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since,
                                             delivery_max_time=loading_dock.time_window.since),
                                         end_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=0,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(hours=2, minutes=15))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(hours=2, minutes=15))))
                                         )

        return [drone_delivery_1, drone_delivery_2]

    @staticmethod
    def _create_drone_deliveries_dock_end(delivery_requests: List[DeliveryRequest],
                                          empty_board: EmptyDroneDeliveryBoard,
                                          loading_dock: DroneLoadingDock) -> List[DroneDelivery]:
        drone_delivery_1 = DroneDelivery(id_=empty_board.empty_drone_deliveries[0].id,
                                         drone_formation=empty_board.empty_drone_deliveries[0].drone_formation,
                                         matched_requests=[
                                             MatchedDeliveryRequest(
                                                 graph_index=0,
                                                 delivery_request=delivery_requests[0],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 35, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 50, 00))),
                                             MatchedDeliveryRequest(
                                                 graph_index=1,
                                                 delivery_request=delivery_requests[1],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 12, 00, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 12, 00, 00)))
                                         ],
                                         start_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=3,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=0))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=0)))),
                                         end_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=3,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=40))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=40)))))

        drone_delivery_2 = DroneDelivery(id_=empty_board.empty_drone_deliveries[1].id,
                                         drone_formation=empty_board.empty_drone_deliveries[1].drone_formation,
                                         matched_requests=[
                                             MatchedDeliveryRequest(
                                                 graph_index=2,
                                                 delivery_request=delivery_requests[2],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 13, 30, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 13, 30, 00)))
                                         ],
                                         start_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=3,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since,
                                             delivery_max_time=loading_dock.time_window.since),
                                         end_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=3,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(hours=2, minutes=15))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(hours=2, minutes=15))))
                                         )

        return [drone_delivery_1, drone_delivery_2]

    @staticmethod
    def _create_drone_deliveries_dock_middle(delivery_requests: List[DeliveryRequest],
                                             empty_board: EmptyDroneDeliveryBoard,
                                             loading_dock: DroneLoadingDock) -> List[DroneDelivery]:
        drone_delivery_1 = DroneDelivery(id_=empty_board.empty_drone_deliveries[0].id,
                                         drone_formation=empty_board.empty_drone_deliveries[0].drone_formation,
                                         matched_requests=[
                                             MatchedDeliveryRequest(
                                                 graph_index=0,
                                                 delivery_request=delivery_requests[0],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 35, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 50, 00))),
                                             MatchedDeliveryRequest(
                                                 graph_index=2,
                                                 delivery_request=delivery_requests[1],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 12, 00, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 12, 00, 00)))
                                         ],
                                         start_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=1,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=0))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=0)))),
                                         end_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=1,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=40))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=40)))))

        drone_delivery_2 = DroneDelivery(id_=empty_board.empty_drone_deliveries[1].id,
                                         drone_formation=empty_board.empty_drone_deliveries[1].drone_formation,
                                         matched_requests=[
                                             MatchedDeliveryRequest(
                                                 graph_index=3,
                                                 delivery_request=delivery_requests[2],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 13, 30, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 13, 30, 00)))
                                         ],
                                         start_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=1,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since,
                                             delivery_max_time=loading_dock.time_window.since),
                                         end_drone_loading_docks=MatchedDroneLoadingDock(
                                             graph_index=1,
                                             drone_loading_dock=loading_dock,
                                             delivery_min_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(hours=2, minutes=15))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(hours=2, minutes=15))))
                                         )

        return [drone_delivery_1, drone_delivery_2]
