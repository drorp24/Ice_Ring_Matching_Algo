import unittest

from time_window import TimeWindow
from datetime import datetime

from common.entities.probabilistic_delivery_requests_generator import create_delivery_requests_dict
from common.graph.operational.delivery_request_graph import DeliveryRequestGraph
from input.delivery_requests_json_converter import create_delivery_request_from_dict


class BasicDeliveryRequestGraphTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.delivery_request_list_1 = [create_delivery_request_from_dict(dr) for dr in create_delivery_requests_dict()]
        cls.delivery_request_list_1_morning_only = [create_delivery_request_from_dict(dr) for dr in create_delivery_requests_dict()]
        cls.delivery_request_list_2 = [create_delivery_request_from_dict(dr) for dr in create_delivery_requests_dict()]
        cls.delivery_request_list_2_low_priority_only = [create_delivery_request_from_dict(dr) for dr in create_delivery_requests_dict()]

    def test_delivery_request_graph_creation(self):
        drg = DeliveryRequestGraph()
        drg.add_delivery_request_nodes(self.delivery_request_list_1)
        drg.add_delivery_request_nodes(self.delivery_request_list_2)
        self.assertEqual(drg.nodes, self.delivery_request_list_1 + self.delivery_request_list_2)

    def test_delivery_request_set_internal_graph(self):
        drg1 = DeliveryRequestGraph()
        drg1.add_delivery_request_nodes(self.delivery_request_list_1)
        drg2 = DeliveryRequestGraph()
        drg2.set_internal_graph(drg1.internal_graph)
        self.assertFalse(drg1.is_empty)
        self.assertEqual(drg1, drg2)

    def test_calc_subgraph_in_time_window(self):
        drg_full_day = DeliveryRequestGraph()
        drg_full_day.add_delivery_request_nodes(self.delivery_request_list_1)
        drg_morning_subgraph_of_full_day = DeliveryRequestGraph()
        drg_morning_subgraph_of_full_day.add_delivery_request_nodes(self.delivery_request_list_1_morning_only)
        morning_time_window = TimeWindow(datetime(2020,1,1,6,0,0), datetime(2020,1,1,12,0,0))
        calculated_subgraph_within_time_window = drg_full_day.calc_subgraph_in_time_window(morning_time_window)
        self.assertTrue(isinstance(calculated_subgraph_within_time_window, DeliveryRequestGraph))
        self.assertEqual(calculated_subgraph_within_time_window, drg_morning_subgraph_of_full_day)

    def test_calc_subgraph_below_priority(self):
        drg_full_day = DeliveryRequestGraph()
        drg_full_day.add_delivery_request_nodes(self.delivery_request_list_2)
        drg_low_priority_subgraph_of_full_day = DeliveryRequestGraph()
        drg_low_priority_subgraph_of_full_day.add_delivery_request_nodes(self.delivery_request_list_1_morning_only)
        max_priority = 10
        calculated_subgraph_below_max_priority = drg_full_day.calc_subgraph_below_priority(max_priority)
        self.assertTrue(isinstance(calculated_subgraph_below_max_priority, DeliveryRequestGraph))
        self.assertEqual(calculated_subgraph_below_max_priority, drg_low_priority_subgraph_of_full_day)