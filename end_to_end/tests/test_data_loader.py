import unittest
from datetime import date, time

from common.entities.temporal import DateTimeExtension
from end_to_end.minimum_end_to_end import MinimumEnd2EndConfig, DataLoader
from end_to_end.scenario import Scenario
#TODO: fix test
#
# class BasicDataLoaderTest(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.minimum_end_2_end_config = MinimumEnd2EndConfig.dict_to_obj(
#             MinimumEnd2EndConfig.json_to_dict('end_to_end/tests/jsons/test_config.json'))
#         cls.data_loader = DataLoader(cls.minimum_end_2_end_config)
#         cls.scenario = Scenario.dict_to_obj(Scenario.json_to_dict('end_to_end/tests/jsons/test_scenario.json'))
#
#     def test_get_delivery_requests(self):
#         delivery_requests = self.data_loader.get_delivery_requests()
#         self.assertEqual(len(delivery_requests), len(self.scenario.delivery_requests))
#         self.assertEqual(delivery_requests, self.scenario.delivery_requests)
#
#     def test_get_fleet_partition(self):
#         empty_drone_delivery_board = self.data_loader.get_empty_drone_delivery_board()
#         self.assertEqual(len(empty_drone_delivery_board.empty_drone_deliveries()),15)
#
#     def test_get_zero_time(self):
#         zero_time_extension = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))
#         zero_time = self.data_loader.get_zero_time()
#         self.assertEqual(zero_time_extension,zero_time)
#
#     def test_get_docks(self):
#         docks_loaded = self.data_loader.get_docks()
#         scenario_dock = self.scenario.drone_loading_docks
#         self.assertEqual(docks_loaded, scenario_dock)
