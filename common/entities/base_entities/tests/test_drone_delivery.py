import unittest
import uuid
from datetime import date, time, timedelta
from random import Random
from typing import List

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import DroneDelivery, EmptyDroneDelivery, MatchedDroneLoadingDock, \
    MatchedDeliveryRequest
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard, \
    UnmatchedDeliveryRequest
from common.entities.base_entities.drone_formation import DroneFormations, DroneFormationType, \
    PackageConfigurationOption
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension, TimeDeltaExtension

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class BasicDroneDeliveryGenerationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        cls.empty_drone_delivery_board = cls._create_empty_board(cls)
        cls.matched_drone_loading_dock = cls._create_expected_single_matched_drone_loading_dock()
        cls.drone_delivery_board = \
            cls._create_drone_delivery_board(cls, cls.delivery_requests,
                                             cls.empty_drone_delivery_board.empty_drone_deliveries,
                                             cls.matched_drone_loading_dock)

    def test_empty_drone_delivery(self):
        self.assertEqual(self.empty_drone_delivery_1.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.empty_drone_delivery_2.drone_formation, DroneFormations.get_drone_formation(
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
        self.assertEqual(self.drone_delivery_1.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.drone_delivery_2.drone_formation, DroneFormations.get_drone_formation(
            DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))

    def test_empty_drone_delivery_board(self):
        self.assertEqual(len(self.empty_drone_delivery_board.empty_drone_deliveries), 2)
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[1].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES,
                             DroneType.drone_type_1))

    def test_drone_delivery_board(self):
        self.assertEqual(len(self.drone_delivery_board.drone_deliveries), 2)
        self.assertEqual(self.drone_delivery_board.drone_deliveries[0].drone_formation,
                         DroneFormations.get_drone_formation(
                             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.drone_delivery_board.drone_deliveries[1].drone_formation,
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

    def test_2_empty_drone_deliveries_are_equal(self):
        actual_empty_drone_delivery = EmptyDroneDelivery(self.entity_id_1, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.assertEqual(self.empty_drone_delivery_1, actual_empty_drone_delivery)

    def test_2_drone_deliveries_are_equal(self):
        actual_drone_delivery = DroneDelivery(self.empty_drone_delivery_1.id,
                                              self.empty_drone_delivery_1.drone_formation,
                                              [self.matched_delivery_request_1, self.matched_delivery_request_2],
                                              self.matched_drone_loading_dock,
                                              self.matched_drone_loading_dock)
        self.assertEqual(self.drone_delivery_1, actual_drone_delivery)

    def test_2_drone_delivery_boards_are_equal(self):
        actual_drone_delivery_board = DroneDeliveryBoard(
            drone_deliveries=[self.drone_delivery_1, self.drone_delivery_2],
            unmatched_delivery_requests=[self.unmatched_delivery_request])
        self.assertEqual(self.drone_delivery_board, actual_drone_delivery_board)

    @staticmethod
    def _create_delivery_requests() -> List[DeliveryRequest]:
        return DeliveryRequestDistribution().choose_rand(random=Random(42), amount={DeliveryRequest: 3})

    def _create_empty_board(self) -> EmptyDroneDeliveryBoard:
        self.entity_id_1 = EntityID(uuid.uuid4())
        self.entity_id_2 = EntityID(uuid.uuid4())
        self.empty_drone_delivery_1 = EmptyDroneDelivery(self.entity_id_1, DroneFormations.get_drone_formation(
            DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        self.empty_drone_delivery_2 = EmptyDroneDelivery(self.entity_id_2, DroneFormations.get_drone_formation(
            DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
        return EmptyDroneDeliveryBoard([self.empty_drone_delivery_1, self.empty_drone_delivery_2])

    @staticmethod
    def _create_expected_single_matched_drone_loading_dock() -> MatchedDroneLoadingDock:
        drone_loading_dock_distribution = DroneLoadingDockDistribution()
        docks = drone_loading_dock_distribution.choose_rand(Random(100), amount=1)
        return MatchedDroneLoadingDock(graph_index=0, drone_loading_dock=docks[0],
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
        self.drone_delivery_1 = DroneDelivery(drone_deliveries[0].id,
                                              drone_deliveries[0].drone_formation,
                                              [self.matched_delivery_request_1, self.matched_delivery_request_2],
                                              matched_drone_loading_dock, matched_drone_loading_dock)
        self.drone_delivery_2 = DroneDelivery(drone_deliveries[1].id,
                                              drone_deliveries[1].drone_formation,
                                              [self.matched_delivery_request_3],
                                              matched_drone_loading_dock, matched_drone_loading_dock)
        return DroneDeliveryBoard(drone_deliveries=[self.drone_delivery_1, self.drone_delivery_2],
                                  unmatched_delivery_requests=[self.unmatched_delivery_request])


# import unittest
# import uuid
# from datetime import date, time, timedelta, datetime
# from random import Random
# from typing import List
#
# from common.entities.base_entities.delivery_request import DeliveryRequest
# from common.entities.base_entities.drone import DroneType
# from common.entities.base_entities.drone_delivery import DroneDelivery, EmptyDroneDelivery, MatchedDeliveryRequest, \
#     MatchedDroneLoadingDock
# from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard, \
#     UnmatchedDeliveryRequest
# from common.entities.base_entities.drone_formation import DroneFormations, PackageConfigurationOption, \
#     DroneFormationType
# from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
# from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
#     DroneLoadingDockDistribution
# from common.entities.base_entities.entity_id import EntityID
# from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension, TimeDeltaExtension
#
# ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))
#
#
# class BasicDroneDeliveryGenerationTests(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.dr = DeliveryRequestDistribution().choose_rand(random=Random(42),
#                                                            amount={DeliveryRequest: 3})
#
#         cls.empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
#             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#         cls.empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
#             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#
#         cls.drone_delivery_1 = DroneDelivery(cls.empty_drone_delivery_1.id,
#                                              cls.empty_drone_delivery_1.drone_formation,
#                                              datetime(2020, 1, 23, 11, 30, 00), [cls.dr[0], cls.dr[1]])
#
#         cls.drone_delivery_2 = DroneDelivery(cls.empty_drone_delivery_2.id,
#                                              cls.empty_drone_delivery_2.drone_formation,
#                                              datetime(2020, 1, 23, 12, 30, 00), [cls.dr[2]])
#
#         cls.empty_drone_delivery_board = EmptyDroneDeliveryBoard(
#             [cls.empty_drone_delivery_1, cls.empty_drone_delivery_2])
#
#         cls.drone_delivery_board = DroneDeliveryBoard([cls.drone_delivery_1, cls.drone_delivery_2])
#
#     def test_delivery_requests_quantity(self):
#         self.assertGreaterEqual(len(self.dr), 3)
#         delivery_requests = self._create_delivery_requests()
#         empty_drone_delivery_board = self._create_empty_board()
#         matched_drone_loading_dock = self._create_expected_single_matched_drone_loading_dock()
#         self.drone_delivery_board = self._create_drone_delivery_board(delivery_requests,
#                                                                       empty_drone_delivery_board.empty_drone_deliveries,
#                                                                       matched_drone_loading_dock)
#
#     def test_empty_drone_delivery(self):
#         self.assertEqual(self.empty_drone_delivery_1.drone_formation, DroneFormations.get_drone_formation(
#             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#         self.assertEqual(self.empty_drone_delivery_2.drone_formation, DroneFormations.get_drone_formation(
#             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#
#     def test_drone_delivery_time_window_output_validation(self):
#         # --- validate first delivery time_window
#         expected_datetime_1 = ZERO_TIME
#         expected_time_window = TimeWindowExtension(expected_datetime_1, expected_datetime_1)
#         self.assertEqual(self.drone_delivery_1.matched_requests[0].delivery_time_window, expected_time_window)
#         self.assertEqual(self.drone_delivery_1.matched_requests[1].delivery_time_window, expected_time_window)
#         # --- validate second delivery time_window
#         expected_datetime_2 = ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=60)))
#         expected_time_window_2 = TimeWindowExtension(expected_datetime_2, expected_datetime_2)
#         self.assertEqual(self.drone_delivery_2.matched_requests[0].delivery_time_window, expected_time_window_2)
#         self.assertEqual(len(self.drone_delivery_2.matched_requests), 1)
#
#     def test_drone_delivery_output_match_request_amount_validation(self):
#         self.assertEqual(len(self.drone_delivery_1.matched_requests), 2)
#
#
#
#     def test_empty_drone_delivery_board(self):
#         self.assertEqual(len(self.empty_drone_delivery_board.empty_drone_deliveries), 2)
#         self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation,
#                          DroneFormations.get_drone_formation(
#                              DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#         self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[1].drone_formation,
#                          DroneFormations.get_drone_formation(
#                              DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES,
#                              DroneType.drone_type_1))
#
#     def test_drone_delivery_board(self):
#         self.assertEqual(len(self.drone_delivery_board.drone_deliveries), 2)
#         self.assertEqual(self.drone_delivery_board.drone_deliveries[0].drone_formation,
#                          DroneFormations.get_drone_formation(
#                              DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#         self.assertEqual(self.drone_delivery_board.drone_deliveries[1].drone_formation,
#                          DroneFormations.get_drone_formation(
#                              DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#
#     def test_2_matched_drone_deliveries_are_equal(self):
#         actual_matched_delivery_request = MatchedDeliveryRequest(
#             graph_index=1,
#             delivery_request=self.dr[0],
#             matched_delivery_option_index=0,
#             delivery_time_window=TimeWindowExtension(
#                 since=ZERO_TIME,
#                 until=ZERO_TIME))
#         self.assertEqual(self.matched_delivery_request_1, actual_matched_delivery_request)
#
#     def test_2_empty_drone_deliveries_are_equal(self):
#         actual_empty_drone_delivery = EmptyDroneDelivery(self.entity_id_1, DroneFormations.get_drone_formation(
#             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#         self.assertEqual(self.empty_drone_delivery_1, actual_empty_drone_delivery)
#
#     def test_2_drone_deliveries_are_equal(self):
#         actual_drone_delivery = DroneDelivery(self.empty_drone_delivery_1.id,
#                                               self.empty_drone_delivery_1.drone_formation,
#                                               [self.matched_delivery_request_1, self.matched_delivery_request_2],
#                                               self.matched_drone_loading_dock,
#                                               self.matched_drone_loading_dock)
#         self.assertEqual(self.drone_delivery_1, actual_drone_delivery)
#
#     def test_2_drone_delivery_boards_are_equal(self):
#         actual_drone_delivery_board = DroneDeliveryBoard(
#             drone_deliveries=[self.drone_delivery_1, self.drone_delivery_2],
#             unmatched_delivery_requests=[self.unmatched_delivery_request])
#         self.assertEqual(self.drone_delivery_board, actual_drone_delivery_board)
#
#     @staticmethod
#     def _create_delivery_requests() -> List[DeliveryRequest]:
#         return DeliveryRequestDistribution().choose_rand(random=Random(42), amount={DeliveryRequest: 3})
#
#     def _create_empty_board(self) -> EmptyDroneDeliveryBoard:
#         self.entity_id_1 = EntityID(uuid.uuid4())
#         self.entity_id_2 = EntityID(uuid.uuid4())
#         self.empty_drone_delivery_1 = EmptyDroneDelivery(self.entity_id_1, DroneFormations.get_drone_formation(
#             DroneFormationType.PAIR, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#         self.empty_drone_delivery_2 = EmptyDroneDelivery(self.entity_id_2, DroneFormations.get_drone_formation(
#             DroneFormationType.QUAD, PackageConfigurationOption.TINY_PACKAGES, DroneType.drone_type_1))
#         return EmptyDroneDeliveryBoard([self.empty_drone_delivery_1, self.empty_drone_delivery_2])
#
#     @staticmethod
#     def _create_expected_single_matched_drone_loading_dock() -> MatchedDroneLoadingDock:
#         drone_loading_dock_distribution = DroneLoadingDockDistribution()
#         docks = drone_loading_dock_distribution.choose_rand(Random(100), amount=1)
#         return MatchedDroneLoadingDock(graph_index=0, drone_loading_dock=docks[0],
#                                        delivery_time_window=TimeWindowExtension(
#                                            since=DateTimeExtension(
#                                                dt_date=date(2020, 1, 23),
#                                                dt_time=time(0, 0, 0)),
#                                            until=DateTimeExtension(
#                                                dt_date=date(2020, 1, 23),
#                                                dt_time=time(23, 59, 59))))
#
#     def _create_drone_delivery_board(self, delivery_requests, drone_deliveries,
#                                      matched_drone_loading_dock) -> DroneDeliveryBoard:
#         self.matched_delivery_request_1 = MatchedDeliveryRequest(
#             graph_index=1,
#             delivery_request=delivery_requests[0],
#             matched_delivery_option_index=0,
#             delivery_time_window=TimeWindowExtension(
#                 since=ZERO_TIME,
#                 until=ZERO_TIME))
#         self.matched_delivery_request_2 = MatchedDeliveryRequest(
#             graph_index=2,
#             delivery_request=delivery_requests[1],
#             matched_delivery_option_index=0,
#             delivery_time_window=TimeWindowExtension(
#                 since=ZERO_TIME,
#                 until=ZERO_TIME))
#         self.matched_delivery_request_3 = MatchedDeliveryRequest(
#             graph_index=3,
#             delivery_request=delivery_requests[2],
#             matched_delivery_option_index=0,
#             delivery_time_window=TimeWindowExtension(
#                 since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=60))),
#                 until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=60)))))
#         self.unmatched_delivery_request = UnmatchedDeliveryRequest(graph_index=4,
#                                                                    delivery_request=delivery_requests[2])
#         self.drone_delivery_1 = DroneDelivery(drone_deliveries[0].id,
#                                               drone_deliveries[0].drone_formation,
#                                               [self.matched_delivery_request_1, self.matched_delivery_request_2],
#                                               matched_drone_loading_dock, matched_drone_loading_dock)
#         self.drone_delivery_2 = DroneDelivery(drone_deliveries[1].id,
#                                               drone_deliveries[1].drone_formation,
#                                               [self.matched_delivery_request_3],
#                                               matched_drone_loading_dock, matched_drone_loading_dock)
#         return DroneDeliveryBoard(drone_deliveries=[self.drone_delivery_1, self.drone_delivery_2],
#                                   unmatched_delivery_requests=[self.unmatched_delivery_request])
