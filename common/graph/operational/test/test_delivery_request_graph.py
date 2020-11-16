import unittest
from datetime import time, date, timedelta
from random import Random

from common.entities.delivery_request import DeliveryRequestDistribution, generate_dr_distribution, PriorityDistribution
from common.entities.delivery_request_generator import DeliveryRequestDatasetGenerator, DeliveryRequestDatasetStructure
from common.entities.temporal import TimeWindowDistribution, DateTimeDistribution, DateTimeExtension, \
    TimeDeltaExtension, TimeDeltaDistribution, TimeWindowExtension
from common.graph.operational.delivery_request_graph import OperationalGraph
from common.graph.operational.graph_creator import create_locally_connected_dr_graph
from geometry.geo_distribution import UniformPointInBboxDistribution


class BasicDeliveryRequestGraphTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(Random(100), 10)
        cls.dr_dataset_morning = create_morning_dr_dataset()
        cls.dr_dataset_afternoon = create_afternoon_dr_dataset()
        cls.dr_dataset_top_priority = create_top_priority_dr_dataset()
        cls.dr_dataset_low_priority = create_low_priority_dr_dataset()
        cls.dr_dataset_local_region_1 = create_local_data_in_region_1()
        cls.dr_dataset_local_region_2 = create_local_data_in_region_2()

    def test_local_graph_generation_should_be_fully_connected(self):
        region_dataset = self.dr_dataset_local_region_1
        g = create_locally_connected_dr_graph(region_dataset, max_dist_to_connect=100)
        num_nodes = len(g.nodes)
        self.assertEqual(len(region_dataset), num_nodes)
        self.assertEqual((num_nodes * (num_nodes - 1)), len(g.edges))

    def test_delivery_request_graph_creation(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_morning)
        drg.add_delivery_requests(self.dr_dataset_afternoon)
        self.assertEqual(_get_dr_from_dr_graph(drg), list(self.dr_dataset_morning) + list(self.dr_dataset_afternoon))

    def test_delivery_request_set_internal_graph(self):
        drg1 = OperationalGraph()
        drg1.add_delivery_requests(self.dr_dataset_random)
        drg2 = OperationalGraph()
        drg2.set_internal_graph(drg1._internal_graph)
        self.assertFalse(drg1.is_empty())
        self.assertEqual(_get_dr_from_dr_graph(drg1), _get_dr_from_dr_graph(drg2))

    def test_calc_subgraph_in_time_window(self):
        drg_full_day = OperationalGraph()
        drg_full_day.add_delivery_requests(self.dr_dataset_morning)
        drg_full_day.add_delivery_requests(self.dr_dataset_afternoon)
        drg_morning_subgraph_of_full_day = OperationalGraph()
        drg_morning_subgraph_of_full_day.add_delivery_requests(self.dr_dataset_morning)
        morning_time_window = TimeWindowExtension(
            since=DateTimeExtension(date(2021, 1, 1), time(6, 0, 0)),
            until=DateTimeExtension(date(2021, 1, 1), time(13, 0, 0)))
        calculated_subgraph_within_time_window = drg_full_day.calc_subgraph_in_time_window(morning_time_window)
        self.assertTrue(isinstance(calculated_subgraph_within_time_window, OperationalGraph))
        nodes_in_time_window_subgraph = _get_dr_from_dr_graph(calculated_subgraph_within_time_window)
        node_in_time_window_morning_graph = _get_dr_from_dr_graph(drg_morning_subgraph_of_full_day)
        self.assertEqual(nodes_in_time_window_subgraph, node_in_time_window_morning_graph)

    def test_calc_subgraph_below_priority(self):
        drg_full_day = OperationalGraph()
        drg_full_day.add_delivery_requests(self.dr_dataset_top_priority)
        drg_full_day.add_delivery_requests(self.dr_dataset_low_priority)
        drg_low_priority_subgraph_of_full_day = OperationalGraph()
        drg_low_priority_subgraph_of_full_day.add_delivery_requests(self.dr_dataset_low_priority)
        max_priority = 10
        calculated_subgraph_below_max_priority = drg_full_day.calc_subgraph_below_priority(max_priority)
        self.assertTrue(isinstance(calculated_subgraph_below_max_priority, OperationalGraph))
        nodes_in_low_priority_subgraph = _get_dr_from_dr_graph(calculated_subgraph_below_max_priority)
        node_in_low_priority_graph = _get_dr_from_dr_graph(drg_low_priority_subgraph_of_full_day)
        self.assertEqual(nodes_in_low_priority_subgraph, node_in_low_priority_graph)


def create_local_data_in_region_1():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                delivery_request_distribution=(_create_region_1_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct)


def create_local_data_in_region_2():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                delivery_request_distribution=(_create_region_2_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct)


def create_morning_dr_dataset():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                delivery_request_distribution=(_create_morning_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct)


def create_afternoon_dr_dataset():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=5,
                                                delivery_request_distribution=(_create_afternoon_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct)


def create_top_priority_dr_dataset():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=4,
                                                delivery_request_distribution=(_create_high_priority_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct)


def create_low_priority_dr_dataset():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=6,
                                                delivery_request_distribution=(_create_low_priority_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct)


def _create_morning_dr_distribution():
    return generate_dr_distribution(
        time_window_distribution=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(6, 0, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3, minutes=30))])))


def _create_afternoon_dr_distribution():
    return generate_dr_distribution(
        time_window_distribution=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(16, 30, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=1, minutes=30))])))


def _create_high_priority_dr_distribution():
    return generate_dr_distribution(priority_distribution=PriorityDistribution([101, 102, 103, 104, 105]))


def _create_low_priority_dr_distribution():
    return generate_dr_distribution(priority_distribution=PriorityDistribution([1, 2, 3, 4, 5]))


def _get_dr_from_dr_graph(drg1):
    return [n.delivery_request for n in drg1.nodes]


def _create_region_1_dr_distribution():
    return generate_dr_distribution(
        drop_point_distribution=UniformPointInBboxDistribution(min_x=100, max_x=200, min_y=50, max_y=150))


def _create_region_2_dr_distribution():
    return generate_dr_distribution(
        drop_point_distribution=UniformPointInBboxDistribution(min_x=1100, max_x=1200, min_y=150, max_y=1150))
