import unittest
import uuid
from datetime import date, time, timedelta
from pathlib import Path
from random import Random
from typing import List

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import DroneDelivery, DeliveringDrones, MatchedDroneLoadingDock, \
    MatchedDeliveryRequest
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard, DroneDeliveryBoard, \
    UnmatchedDeliveryRequest
from common.entities.base_entities.drone_formation import DroneFormations, DroneFormationType, \
    PackageConfigurationOption
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.drone_distribution import DroneTypeDistribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension, TimeDeltaExtension

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class BasicDroneDeliveryGenerationTests(unittest.TestCase):
    drone_delivery_board_json_path = Path('common/entities/base_entities/tests/delivery_board_test_file.json')
    delivering_drones_json_path = Path('common/entities/base_entities/tests/delivering_drones_test_file.json')

    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        drone_type_distribution = DroneTypeDistribution({DroneType.drone_type_1: 1})
        cls.docks = DroneLoadingDockDistribution(
            drone_type_distribution=drone_type_distribution).choose_rand(Random(100), amount=1)
        cls.delivering_drones_board = cls._create_delivering_drones_board(cls)
        cls.matched_drone_loading_dock = cls._create_expected_single_matched_drone_loading_dock(cls)
        cls.drone_delivery_board = \
            cls._create_drone_delivery_board(cls, cls.delivery_requests,
                                             cls.delivering_drones_board.delivering_drones_list,
                                             cls.matched_drone_loading_dock)

    @classmethod
    def tearDownClass(cls):
        cls.drone_delivery_board_json_path.unlink()
        cls.delivering_drones_json_path.unlink()

    def test_delivering_drones(self):
        self.assertEqual(self.delivering_drones_1.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.delivering_drones_2.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))

    def test_drone_delivery_time_window_output_validation(self):
        # --- validate first delivery time_window
        expected_datetime_1 = ZERO_TIME
        expected_time_window = TimeWindowExtension(expected_datetime_1, expected_datetime_1)
        self.assertEqual(self.drone_delivery_1.matched_requests[0].delivery_time_window, expected_time_window)
        self.assertEqual(self.drone_delivery_1.matched_requests[1].delivery_time_window, expected_time_window)
        # --- validate second delivery time_window
        expected_datetime_2 = ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=60)))
        expected_time_window_2 = TimeWindowExtension(expected_datetime_2, expected_datetime_2)
        self.assertEqual(self.drone_delivery_2.matched_requests[0].delivery_time_window, expected_time_window_2)
        self.assertEqual(len(self.drone_delivery_2.matched_requests), 1)

    def test_drone_delivery_output_match_request_amount_validation(self):
        self.assertEqual(len(self.drone_delivery_1.matched_requests), 2)

    def test_drone_delivery_output_formation_validation(self):
        self.assertEqual(self.drone_delivery_1.delivering_drones.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.drone_delivery_2.delivering_drones.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))

    def test_delivering_drones_board(self):
        self.assertEqual(len(self.delivering_drones_board.delivering_drones_list), 2)
        self.assertEqual(self.delivering_drones_board.delivering_drones_list[0].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.delivering_drones_board.delivering_drones_list[1].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES,
                             DroneType.drone_type_1))

    def test_drone_delivery_board(self):
        self.assertEqual(len(self.drone_delivery_board.drone_deliveries), 2)
        self.assertEqual(self.drone_delivery_board.drone_deliveries[0].delivering_drones.drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.drone_delivery_board.drone_deliveries[1].delivering_drones.drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))

    def test_2_matched_drone_deliveries_are_equal(self):
        actual_matched_delivery_request = MatchedDeliveryRequest(
            graph_index=1,
            delivery_request=self.delivery_requests[0],
            matched_delivery_option_index=0,
            delivery_time_window=TimeWindowExtension(
                since=ZERO_TIME,
                until=ZERO_TIME))

        self.assertEqual(self.matched_delivery_request_1, actual_matched_delivery_request)

    def test_2_delivering_drones_list_are_equal(self):
        actual_delivering_drones = DeliveringDrones(id_=self.entity_id_1,
                                                       drone_formation=DroneFormations.get_drone_formation(
                                                           DroneFormationType.PAIR,
                                                           PackageConfigurationOption.TINY_PACKAGES,
                                                           DroneType.drone_type_1),
                                                       start_loading_dock=self.docks[0],
                                                       end_loading_dock=self.docks[0])
        self.assertEqual(self.delivering_drones_1, actual_delivering_drones)

    def test_2_drone_deliveries_are_equal(self):
        actual_drone_delivery = DroneDelivery(self.delivering_drones_1,
                                              [self.matched_delivery_request_1, self.matched_delivery_request_2],
                                              self.matched_drone_loading_dock,
                                              self.matched_drone_loading_dock)
        self.assertEqual(self.drone_delivery_1, actual_drone_delivery)

    def test_2_drone_delivery_boards_are_equal(self):
        actual_drone_delivery_board = DroneDeliveryBoard(
            drone_deliveries=[self.drone_delivery_1, self.drone_delivery_2],
            unmatched_delivery_requests=[self.unmatched_delivery_request])
        self.assertEqual(self.drone_delivery_board, actual_drone_delivery_board)

    def test_drone_delivery_board_to_json_and_back_to_drone_delivery_board(self):
        self.drone_delivery_board.to_json(self.drone_delivery_board_json_path)

        drone_delivery_board_from_json = DroneDeliveryBoard.from_json(self.drone_delivery_board_json_path)
        self.assertEqual(self.drone_delivery_board, drone_delivery_board_from_json)

    def test_delivering_drones_is_jsonable(self):
        self.delivering_drones_1.to_json(self.delivering_drones_json_path)

        delivering_drones_from_json = DeliveringDrones.from_json(self.delivering_drones_json_path)
        self.assertEqual(self.delivering_drones_1, delivering_drones_from_json)

    @staticmethod
    def _create_delivery_requests() -> List[DeliveryRequest]:
        return DeliveryRequestDistribution().choose_rand(random=Random(42), amount={DeliveryRequest: 3})

    def _create_delivering_drones_board(self) -> DeliveringDronesBoard:
        self.entity_id_1 = EntityID(uuid.uuid4())
        self.entity_id_2 = EntityID(uuid.uuid4())
        self.delivering_drones_1 = DeliveringDrones(id_=self.entity_id_1,
                                                       drone_formation=DroneFormations.get_drone_formation(
                                                           DroneFormationType.PAIR,
                                                           PackageConfigurationOption.TINY_PACKAGES,
                                                           DroneType.drone_type_1),
                                                       start_loading_dock=self.docks[0],
                                                       end_loading_dock=self.docks[0])
        self.delivering_drones_2 = DeliveringDrones(id_=self.entity_id_2,
                                                       drone_formation=DroneFormations.get_drone_formation(
                                                           DroneFormationType.QUAD,
                                                           PackageConfigurationOption.TINY_PACKAGES,
                                                           DroneType.drone_type_1),
                                                       start_loading_dock=self.docks[0],
                                                       end_loading_dock=self.docks[0])
        return DeliveringDronesBoard([self.delivering_drones_1, self.delivering_drones_2])

    @staticmethod
    def _create_expected_single_matched_drone_loading_dock(cls) -> MatchedDroneLoadingDock:
        return MatchedDroneLoadingDock(drone_loading_dock=cls.docks[0],
                                       delivery_time_window=TimeWindowExtension(
                                           since=DateTimeExtension(
                                               dt_date=date(2020, 1, 23),
                                               dt_time=time(0, 0, 0)),
                                           until=DateTimeExtension(
                                               dt_date=date(2020, 1, 23),
                                               dt_time=time(23, 59, 59))))

    def _create_drone_delivery_board(self, delivery_requests, drone_deliveries,
                                     matched_drone_loading_dock) -> DroneDeliveryBoard:
        self.matched_delivery_request_1 = MatchedDeliveryRequest(
            graph_index=1,
            delivery_request=delivery_requests[0],
            matched_delivery_option_index=0,
            delivery_time_window=TimeWindowExtension(
                since=ZERO_TIME,
                until=ZERO_TIME))
        self.matched_delivery_request_2 = MatchedDeliveryRequest(
            graph_index=2,
            delivery_request=delivery_requests[1],
            matched_delivery_option_index=0,
            delivery_time_window=TimeWindowExtension(
                since=ZERO_TIME,
                until=ZERO_TIME))
        self.matched_delivery_request_3 = MatchedDeliveryRequest(
            graph_index=3,
            delivery_request=delivery_requests[2],
            matched_delivery_option_index=0,
            delivery_time_window=TimeWindowExtension(
                since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=60))),
                until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=60)))))
        self.unmatched_delivery_request = UnmatchedDeliveryRequest(graph_index=4,
                                                                   delivery_request=delivery_requests[2])
        self.drone_delivery_1 = DroneDelivery(drone_deliveries[0],
                                              [self.matched_delivery_request_1, self.matched_delivery_request_2],
                                              matched_drone_loading_dock, matched_drone_loading_dock)
        self.drone_delivery_2 = DroneDelivery(drone_deliveries[1],
                                              [self.matched_delivery_request_3],
                                              matched_drone_loading_dock, matched_drone_loading_dock)
        return DroneDeliveryBoard(drone_deliveries=[self.drone_delivery_1, self.drone_delivery_2],
                                  unmatched_delivery_requests=[self.unmatched_delivery_request])
