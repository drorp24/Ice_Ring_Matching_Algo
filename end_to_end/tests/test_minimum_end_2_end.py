import unittest

from common.entities.package import PackageType
from end_to_end.minimum_end_to_end import MinimumEnd2EndConfig, DataLoader, MinimumEnd2End


class BasicMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.minimum_end_2_end_config = MinimumEnd2EndConfig.dict_to_obj(
            MinimumEnd2EndConfig.json_to_dict('end_to_end/tests/jsons/test_config.json'))
        cls.data_loader = DataLoader(cls.minimum_end_2_end_config)
        cls.minimum_end_2_end = MinimumEnd2End(cls.data_loader.get_scenario(), cls.data_loader.get_empty_drone_delivery_board())

    def test_create_graph_model(self):
        operational_graph = self.minimum_end_2_end.create_fully_connected_graph_model()
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    def test_calc_assignment(self):
        operational_graph = self.minimum_end_2_end.create_fully_connected_graph_model()
        delivery_board = self.minimum_end_2_end.calc_assignment(operational_graph,
                                                                self.minimum_end_2_end_config.matcher_config_json)
        self.assertEqual(len(delivery_board.dropped_delivery_requests), 4)
        self.assertEqual(len(delivery_board.total_amount_per_package_type.get_package_type_volume(PackageType.TINY)), 1)
        self.assertEqual(len(delivery_board.total_amount_per_package_type.get_package_type_volume(PackageType.MEDIUM)), 1)
        self.assertEqual(len(delivery_board.total_amount_per_package_type.get_package_type_volume(PackageType.LARGE), 4))
        self.assertEqual(delivery_board.total_priority(), 477)

