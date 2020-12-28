from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from unittest import TestCase
from uuid import UUID

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PlatformType
from common.entities.base_entities.drone_delivery import EmptyDroneDelivery, DroneDelivery, MatchedDeliveryRequest, \
    MatchedDroneLoadingDock
from common.entities.base_entities.drone_delivery_board import DroppedDeliveryRequest, DroneDeliveryBoard, \
    EmptyDroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormations, FormationOptions, FormationSize
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.base_entities.temporal import TimeWindowExtension, DateTimeExtension, TimeDeltaExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher

ZERO_TIME = datetime(2020, 1, 23, 11, 30, 00)


class ORToolsMatcherDifferentPriorityTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        cls.loading_dock = cls._create_loading_dock()
        cls.graph = cls._create_graph(cls.delivery_requests, cls.loading_dock)
        cls.empty_board = cls._create_empty_board()
        cls.match_input = cls._create_match_input(cls.graph, cls.empty_board)

    def test_matcher(self):
        matcher = ORToolsMatcher(self.match_input)
        actual_delivery_board = matcher.match()
        expected_drone_deliveries = self._create_drone_deliveries(delivery_requests=self.delivery_requests,
                                                                  empty_board=self.empty_board,
                                                                  loading_dock=self.loading_dock)

        dropped_delivery_request = DroppedDeliveryRequest(graph_index=2, delivery_request=self.delivery_requests[1])

        expected_matched_board = DroneDeliveryBoard(
            drone_deliveries=[expected_drone_deliveries[0]],
            dropped_delivery_requests=[dropped_delivery_request])

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
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
            priority=1)

        delivery_request_2 = DeliveryRequest(
            delivery_options=[DeliveryOption([CustomerDelivery([
                PackageDeliveryPlan(UUID(int=2),
                                    create_point_2d(0, 10),
                                    Angle(45, AngleUnit.DEGREE),
                                    Angle(45, AngleUnit.DEGREE),
                                    PackageType.LARGE)])])],
            time_window=TimeWindowExtension(
                since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
            priority=10)

        delivery_request_3 = DeliveryRequest(
            delivery_options=[DeliveryOption([CustomerDelivery([
                PackageDeliveryPlan(UUID(int=3),
                                    create_point_2d(0, 15),
                                    Angle(45, AngleUnit.DEGREE),
                                    Angle(45, AngleUnit.DEGREE),
                                    PackageType.LARGE)])])],
            time_window=TimeWindowExtension(
                since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
            priority=1)

        return [delivery_request_1, delivery_request_2, delivery_request_3]

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
                                PlatformType.platform_1,
                                TimeWindowExtension(
                                    since=DateTimeExtension.from_dt(ZERO_TIME),
                                    until=DateTimeExtension.from_dt(ZERO_TIME).add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=1)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock) -> OperationalGraph:
        graph = OperationalGraph(zero_time=ZERO_TIME)
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
    def _create_match_input(graph: OperationalGraph, empty_board: EmptyDroneDeliveryBoard) -> MatcherInput:
        do_dict = JsonableBaseEntity.json_to_dict(Path('matching/test/jsons/test_matcher_config_1.json'))
        match_config_properties = MatcherConfig.dict_to_obj(do_dict)
        return MatcherInput(graph, empty_board, match_config_properties)

    @staticmethod
    def _create_drone_deliveries(delivery_requests: List[DeliveryRequest], empty_board: EmptyDroneDeliveryBoard,
                                 loading_dock: DroneLoadingDock) -> List[DroneDelivery]:
        drone_delivery_1 = DroneDelivery(id_=empty_board.empty_drone_deliveries[0].id,
                                         drone_formation=empty_board.empty_drone_deliveries[0].drone_formation,
                                         matched_requests=[MatchedDeliveryRequest(
                                             graph_index=3,
                                             delivery_request=delivery_requests[2],
                                             matched_delivery_option_index=0,
                                             delivery_min_time=DateTimeExtension.from_dt(
                                                 datetime(2020, 1, 23, 11, 45, 00)),
                                             delivery_max_time=DateTimeExtension.from_dt(
                                                 datetime(2020, 1, 23, 11, 45, 00))),
                                             MatchedDeliveryRequest(
                                                 graph_index=1,
                                                 delivery_request=delivery_requests[0],
                                                 matched_delivery_option_index=0,
                                                 delivery_min_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 55, 00)),
                                                 delivery_max_time=DateTimeExtension.from_dt(
                                                     datetime(2020, 1, 23, 11, 55, 00)))
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
                                                 TimeDeltaExtension(timedelta(minutes=30))),
                                             delivery_max_time=loading_dock.time_window.since.add_time_delta(
                                                 TimeDeltaExtension(timedelta(minutes=30))))
                                         )

        return [drone_delivery_1]
