from pathlib import Path
from unittest import TestCase, mock
from datetime import datetime

from common.entities.drone import PlatformType
from common.entities.drone_delivery import DroneDelivery, EmptyDroneDelivery, MatchedDeliveryRequest
from common.entities.drone_delivery_board import DroneDeliveryBoard, EmptyDroneDeliveryBoard
from common.entities.drone_formation import FormationSize, FormationOptions, DroneFormations
from input.delivery_requests_json_converter import create_delivery_requests_from_file
from matching.matcher import MatchInput, MatchConfig
from matching.ortools.ortools_matcher import ORToolsMatcher


class TestORToolsMatcher(TestCase):

    @staticmethod
    def create_graph_mock(delivery_requests):
        def mock_get_delivery_request(node_index):
            return delivery_requests[node_index]

        small_graph = mock.Mock()
        small_graph.configure_mock(zero_time=datetime(2020, 1, 23, 11, 30, 00),
                                   priorities=[0, 1, 2],
                                   packages_per_request=[0, 1, 1],
                                   travel_weights=[
                                       [0, 3, 6],
                                       [3, 0, 5],
                                       [6, 5, 0],
                                   ],
                                   depos=0,
                                   time_windows=[
                                       (0, 300),  # depot
                                       (0, 30),  # 1
                                       (60, 75),  # 2
                                   ],
                                   get_delivery_request=mock_get_delivery_request)
        return small_graph

    @staticmethod
    def create_empty_drone_delivery_board():
        empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))
        empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
            FormationSize.MEDIUM, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))

        return EmptyDroneDeliveryBoard([empty_drone_delivery_1, empty_drone_delivery_2])

    @staticmethod
    def create_drone_delivery_board(empty_drone_delivery_1, empty_drone_delivery_2, delivery_requests):
        drone_delivery_1 = DroneDelivery(empty_drone_delivery_1.id,
                                         empty_drone_delivery_1.drone_formation)
        drone_delivery_1.add_matched_delivery_request(MatchedDeliveryRequest(delivery_requests[0],
                                                                             datetime(2020, 1, 23, 11, 33, 00)))
        drone_delivery_2 = DroneDelivery(empty_drone_delivery_2.id,
                                         empty_drone_delivery_2.drone_formation)
        drone_delivery_2.add_matched_delivery_request(MatchedDeliveryRequest(delivery_requests[1],
                                                                             datetime(2020, 1, 23, 12, 30, 00)))

        return DroneDeliveryBoard([drone_delivery_1, drone_delivery_2])

    @classmethod
    def setUpClass(cls):
        delivery_requests = create_delivery_requests_from_file(Path('delivery_requests1.json'))
        small_graph = cls.create_graph_mock(delivery_requests)  # TODO: create real graph
        empty_board = cls.create_empty_drone_delivery_board()
        config = MatchConfig.from_file(Path('match_config1.json'))

        cls.small_match_input = MatchInput(small_graph, empty_board, config)
        cls.expected_matched_board = cls.create_drone_delivery_board(empty_board.empty_drone_deliveries[0],
                                                                     empty_board.empty_drone_deliveries[1],
                                                                     delivery_requests)

    def test_match(self):
        matcher = ORToolsMatcher(self.small_match_input)
        solution = matcher.match()
        solution.print_solution()
        actual_delivery_board = solution.delivery_board()
        self.assertEqual(self.expected_matched_board, actual_delivery_board)
