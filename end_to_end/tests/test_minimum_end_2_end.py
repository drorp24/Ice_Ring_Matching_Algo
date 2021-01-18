import unittest

from common.entities.base_entities.package import PackageType
from common.tools.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.tools.fleet_reader import FleetReader
from end_to_end.minimum_end_to_end import create_fully_connected_graph_model, calc_assignment
from end_to_end.scenario import Scenario
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput


class BasicMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scenario = Scenario.dict_to_obj(Scenario.json_to_dict('end_to_end/tests/jsons/test_scenario.json'))
        cls.empty_drone_delivery_board = generate_empty_delivery_board(
            FleetReader('end_to_end/tests/jsons/test_fleet.json'))
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict('end_to_end/tests/jsons/test_matcher_config.json'))

    def test_create_graph_model(self):
        operational_graph = create_fully_connected_graph_model(self.scenario)
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    def test_calc_assignment(self):
        operational_graph = create_fully_connected_graph_model(self.scenario)
        matcher_input = MatcherInput(graph=operational_graph,
                                     empty_board=self.empty_drone_delivery_board,
                                     config=self.matcher_config)

        delivery_board = calc_assignment(matcher_input=matcher_input)
        self.assertEqual(len(delivery_board.unmatched_delivery_requests), 4)
        self.assertEqual(delivery_board.get_total_amount_per_package_type().get_package_type_amount(PackageType.TINY), 1)
        self.assertEqual(delivery_board.get_total_amount_per_package_type().get_package_type_amount(PackageType.MEDIUM), 1)
        self.assertEqual(delivery_board.get_total_amount_per_package_type().get_package_type_amount(PackageType.LARGE), 4)
        self.assertEqual(delivery_board.get_total_priority(), 477)
