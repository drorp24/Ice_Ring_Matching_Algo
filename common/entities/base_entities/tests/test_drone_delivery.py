import unittest
from datetime import date, time
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PlatformType
from common.entities.base_entities.drone_delivery import DroneDelivery, EmptyDroneDelivery, MatchedDroneLoadingDock, \
    MatchedDeliveryRequest
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.drone_formation import DroneFormations, FormationSize, FormationOptions
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.temporal import DateTimeExtension


class BasicDroneDeliveryGenerationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = DeliveryRequestDistribution().choose_rand(random=Random(42), amount={DeliveryRequest: 3})

        cls.empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))
        cls.empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
            FormationSize.MEDIUM, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))

        cls.matched_delivery_request_1 = MatchedDeliveryRequest(
            graph_index=1,
            delivery_request=cls.delivery_requests[0],
            matched_delivery_option_index=0,
            delivery_min_time=DateTimeExtension(
                dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)),
            delivery_max_time=DateTimeExtension(
                dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)))

        cls.matched_delivery_request_2 = MatchedDeliveryRequest(
            graph_index=2,
            delivery_request=cls.delivery_requests[1],
            matched_delivery_option_index=0,
            delivery_min_time=DateTimeExtension(
                dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)),
            delivery_max_time=DateTimeExtension(
                dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0)))

        cls.matched_delivery_request_3 = MatchedDeliveryRequest(
            graph_index=3,
            delivery_request=cls.delivery_requests[2],
            matched_delivery_option_index=0,
            delivery_min_time=DateTimeExtension(
                dt_date=date(2020, 1, 23), dt_time=time(12, 30, 0)),
            delivery_max_time=DateTimeExtension(
                dt_date=date(2020, 1, 23), dt_time=time(12, 30, 0)))

        cls.unmatched_delivery_request = UnmatchedDeliveryRequest(graph_index=4, delivery_request=cls.delivery_requests[2])

        drone_loading_dock_distribution = DroneLoadingDockDistribution()
        docks = drone_loading_dock_distribution.choose_rand(Random(100), amount=1)
        cls.matched_drone_loading_dock = MatchedDroneLoadingDock(graph_index=0, drone_loading_dock=docks[0],
                                                                 delivery_min_time=DateTimeExtension(
                                                                     dt_date=date(2020, 1, 23),
                                                                     dt_time=time(0, 0, 0)),
                                                                 delivery_max_time=DateTimeExtension(
                                                                     dt_date=date(2020, 1, 23),
                                                                     dt_time=time(23, 59, 59)))

        cls.drone_delivery_1 = DroneDelivery(cls.empty_drone_delivery_1.id,
                                             cls.empty_drone_delivery_1.drone_formation,
                                             [cls.matched_delivery_request_1, cls.matched_delivery_request_2],
                                             cls.matched_drone_loading_dock, cls.matched_drone_loading_dock)
        cls.drone_delivery_2 = DroneDelivery(cls.empty_drone_delivery_2.id,
                                             cls.empty_drone_delivery_2.drone_formation,
                                             [cls.matched_delivery_request_3],
                                             cls.matched_drone_loading_dock, cls.matched_drone_loading_dock)

        cls.empty_drone_delivery_board = EmptyDroneDeliveryBoard(
            [cls.empty_drone_delivery_1, cls.empty_drone_delivery_2])

        cls.drone_delivery_board = DroneDeliveryBoard(drone_deliveries=[cls.drone_delivery_1, cls.drone_delivery_2],
                                                      unmatched_delivery_requests=[cls.unmatched_delivery_request])

    def test_empty_drone_delivery(self):
        self.assertEqual(self.empty_drone_delivery_1.drone_formation, DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))
        self.assertEqual(self.empty_drone_delivery_2.drone_formation, DroneFormations.get_drone_formation(
            FormationSize.MEDIUM, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))

    def test_drone_delivery(self):
        self.assertEqual(self.drone_delivery_1.drone_formation, DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))

        expected_datetime_1 = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))

        self.assertEqual(self.drone_delivery_1.matched_requests[0].delivery_min_time, expected_datetime_1)
        self.assertEqual(self.drone_delivery_1.matched_requests[0].delivery_max_time, expected_datetime_1)
        self.assertEqual(self.drone_delivery_1.matched_requests[1].delivery_min_time, expected_datetime_1)
        self.assertEqual(self.drone_delivery_1.matched_requests[1].delivery_max_time, expected_datetime_1)
        self.assertEqual(len(self.drone_delivery_1.matched_requests), 2)

        self.assertEqual(self.drone_delivery_2.drone_formation, DroneFormations.get_drone_formation(
            FormationSize.MEDIUM, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))

        expected_datetime_2 = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(12, 30, 0))
        self.assertEqual(self.drone_delivery_2.matched_requests[0].delivery_min_time, expected_datetime_2)
        self.assertEqual(self.drone_delivery_2.matched_requests[0].delivery_max_time, expected_datetime_2)
        self.assertEqual(len(self.drone_delivery_2.matched_requests), 1)

    def test_empty_drone_delivery_board(self):
        self.assertEqual(len(self.empty_drone_delivery_board.empty_drone_deliveries), 2)
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation,
                         DroneFormations.get_drone_formation(
                             FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))
        self.assertEqual(self.empty_drone_delivery_board.empty_drone_deliveries[1].drone_formation,
                         DroneFormations.get_drone_formation(
                             FormationSize.MEDIUM, FormationOptions.TINY_PACKAGES,
                             PlatformType.platform_1))

    def test_drone_delivery_board(self):
        self.assertEqual(len(self.drone_delivery_board.drone_deliveries), 2)
        self.assertEqual(self.drone_delivery_board.drone_deliveries[0].drone_formation,
                         DroneFormations.get_drone_formation(
                             FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))
        self.assertEqual(self.drone_delivery_board.drone_deliveries[1].drone_formation,
                         DroneFormations.get_drone_formation(
                             FormationSize.MEDIUM, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))

    def test_2_matched_drone_deliveries_are_equal(self):
        actual_matched_delivery_request = MatchedDeliveryRequest(
            graph_index=1,
            delivery_request=self.delivery_requests[0],
            matched_delivery_option_index=0,
            delivery_min_time=DateTimeExtension(
                dt_date=date(2020, 1, 23),
                dt_time=time(11, 30, 0)),
            delivery_max_time=DateTimeExtension(
                dt_date=date(2020, 1, 23),
                dt_time=time(11, 30, 0)))

        self.assertEqual(self.matched_delivery_request_1, actual_matched_delivery_request)

    def test_2_empty_drone_deliveries_are_equal(self):
        actual_empty_drone_delivery = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))
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
