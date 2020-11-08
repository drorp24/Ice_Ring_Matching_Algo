from unittest import TestCase, mock

from matching.matcher import MatchInput, MatchConfig
from matching.ortools.ortools_matcher import ORToolsMatcher


class TestORToolsMatcher(TestCase):

    @classmethod
    def setUpClass(cls):
        small_graph = mock.Mock()
        small_graph.configure_mock(priorities=[0, 1, 2],
                             packeges_per_request=[0, 1, 2],
                             travel_weights=[
                                 [0, 6, 9],
                                 [6, 0, 8],
                                 [9, 8, 0],
                             ],
                             depos=0,
                             time_windows=[
                                 (0, 5),  # depot
                                 (7, 12),  # 1
                                 (10, 15),  # 2
                             ])
        empty_board = mock.Mock()
        empty_board.configure_mock(empty_drone_deliveries=[15, 15],
                                   vehicle_capacities=[15, 15],
                                   num_of_formations=2)
        config = MatchConfig.from_file("match_config1.json")

        cls.small_match_input = MatchInput(small_graph, empty_board, config)

    def test_match(self):
        expected_delivery_board = DeliveryBoard()
        matcher = ORToolsMatcher(self.small_match_input)
        solution = matcher.match()
        solution.print_solution()
        self.assertEqual(solution.delivery_board(), expected_delivery_board)
        # self.assertEqual(self.PLATFORM_1_2X8.platform_type, PlatformType.platform_1)
