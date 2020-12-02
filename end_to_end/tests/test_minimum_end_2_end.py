import unittest

from end_to_end.minimum_end_to_end import MinimumEnd2EndConfig, DataLoader, MinimumEnd2End


class BasicMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.minimum_end_2_end_config = MinimumEnd2EndConfig.dict_to_obj(
            MinimumEnd2EndConfig.json_to_dict('end_to_end/tests/jsons/test_config.json'))
        cls.data_loader = DataLoader(cls.minimum_end_2_end_config)
        cls.minimum_end_2_end = MinimumEnd2End(cls.data_loader)

    def test_create_graph_model(self):
        max_cost = 10
        operational_graph = self.minimum_end_2_end.create_graph_model(max_cost)
        self.assertEqual(len(operational_graph.nodes),11)

    def test_calc_assignment(self):
        max_cost = 10
        operational_graph = self.minimum_end_2_end.create_graph_model(max_cost)
        delivery_board = self.minimum_end_2_end.calc_assignment(operational_graph, self.minimum_end_2_end_config.matcher_config_json)
        self.assertEqual(10,10)

