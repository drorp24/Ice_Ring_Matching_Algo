from unittest import TestCase, mock

from matching.matcher import MatchInput, MatchConfig
from matching.ortools.ortools_matcher import ORToolsMatcher


class TestORToolsMatcher(TestCase):

    @classmethod
    def setUpClass(cls):
        graph = mock.Mock()
        graph.configure_mock(priorities=[0, 8, 8, 2, 4, 2, 4, 3, 3, 1, 5, 1, 2, 4, 8, 3, 8],
                             packeges_per_request=[0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8],
                             travel_weights=[
                                 [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
                                 [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
                                 [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
                                 [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
                                 [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
                                 [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
                                 [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
                                 [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
                                 [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
                                 [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
                                 [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
                                 [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
                                 [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
                                 [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
                                 [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
                                 [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
                                 [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
                             ],
                             depos=0,
                             time_windows=[
                                 (0, 5),  # depot
                                 (7, 12),  # 1
                                 (10, 15),  # 2
                                 (16, 18),  # 3
                                 (10, 13),  # 4
                                 (0, 5),  # 5
                                 (5, 10),  # 6
                                 (0, 4),  # 7
                                 (5, 10),  # 8
                                 (0, 3),  # 9
                                 (10, 16),  # 10
                                 (10, 15),  # 11
                                 (0, 5),  # 12
                                 (5, 10),  # 13
                                 (7, 8),  # 14
                                 (10, 15),  # 15
                                 (11, 15),  # 16
                             ])
        empty_board = mock.Mock()
        empty_board.configure_mock(empty_drone_deliveries=[15, 15, 15, 15],
                                   vehicle_capacities=[15, 15, 15, 15],
                                   num_of_formations=4)
        config = MatchConfig.from_file("match_input.json")

        cls.match_input = MatchInput(graph, empty_board, config)

    def test_match(self):
        matcher = ORToolsMatcher(self.match_input)
        solution = matcher.match()
        solution.print_solution()
        # self.assertEqual(self.PLATFORM_1_2X8.platform_type, PlatformType.platform_1)
