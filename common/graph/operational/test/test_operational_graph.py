import unittest
from datetime import time, date, timedelta
from math import sqrt
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution, \
    PriorityDistribution
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    TimeWindowDistribution, DateTimeDistribution
from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension, TimeWindowExtension
from common.entities.generator.delivery_request_generator import DeliveryRequestDatasetGenerator, \
    DeliveryRequestDatasetStructure
from common.graph.operational.graph_creator import add_locally_connected_dr_graph, add_fully_connected_loading_docks
from common.graph.operational.operational_graph import OperationalEdge, \
    OperationalEdgeAttribs, OperationalNode, NonLocalizableNodeException, NonTemporalNodeException
from common.graph.operational.operational_graph import OperationalGraph
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import create_point_2d, create_polygon_2d


class BasicDeliveryRequestGraphTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(random=Random(100), amount={DeliveryRequest: 10})
        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(random=Random(100), amount=3)
        cls.dr_dataset_morning = create_morning_dr_dataset()
        cls.dr_dataset_afternoon = create_afternoon_dr_dataset()
        cls.dr_dataset_top_priority = create_top_priority_dr_dataset()
        cls.dr_dataset_low_priority = create_low_priority_dr_dataset()
        cls.dr_dataset_local_region_1_morning = create_local_data_in_region_1_morning()
        cls.dr_dataset_local_region_2_morning = create_local_data_in_region_2_morning()
        cls.dr_dataset_local_region_2_afternoon = create_local_data_in_region_2_afternoon()
        cls.radius_surrounding_region_1 = 100 * 2 / sqrt(2)

    def test_localizable_node_exception(self):
        with self.assertRaises(NonLocalizableNodeException) as context:
            OperationalNode(3)

    def test_temporal_node_exception(self):
        with self.assertRaises(NonTemporalNodeException) as context:
            OperationalNode(DeliveryOptionDistribution().choose_rand(Random(42))[0])

    def test_local_graph_generation_should_be_fully_connected(self):
        region_dataset = self.dr_dataset_local_region_1_morning
        graph = OperationalGraph()
        add_locally_connected_dr_graph(graph, region_dataset, max_cost_to_connect=self.radius_surrounding_region_1)
        num_nodes = len(graph.nodes)
        self.assertEqual(len(region_dataset), num_nodes)
        self.assertEqual((num_nodes * (num_nodes - 1)), len(graph.edges))

    def test_local_graph_generation_two_separate_spatial_cliques(self):
        region_dataset = self.dr_dataset_local_region_1_morning + self.dr_dataset_local_region_2_morning
        graph = OperationalGraph()
        add_locally_connected_dr_graph(graph, region_dataset, max_cost_to_connect=self.radius_surrounding_region_1)
        num_nodes_in_graph = len(graph.nodes)
        self.assertEqual(len(region_dataset), num_nodes_in_graph)
        self.assertEqual(2 * (num_nodes_in_graph / 2 * (num_nodes_in_graph / 2 - 1)), len(graph.edges))

    def test_local_graph_generation_two_separate_temporal_cliques(self):
        region_dataset = self.dr_dataset_local_region_2_afternoon + self.dr_dataset_local_region_2_morning
        graph = OperationalGraph()
        add_locally_connected_dr_graph(graph, region_dataset, max_cost_to_connect=self.radius_surrounding_region_1)
        num_nodes = len(graph.nodes)
        self.assertEqual(len(region_dataset), num_nodes)
        self.assertEqual(2 * (num_nodes / 2 * (num_nodes / 2 - 1)), len(graph.edges))

    def test_add_full_connection_between_loading_docks_and_delivery_requests(self):
        regional_dr_dataset = self.dr_dataset_local_region_2_afternoon
        graph = OperationalGraph()
        graph.add_delivery_requests(regional_dr_dataset)
        dld_dataset = create_loading_dock_afternoon_distribution()
        add_fully_connected_loading_docks(graph, dld_dataset)
        self.assertEqual(len(regional_dr_dataset) + len(dld_dataset), len(graph.nodes))
        self.assertEqual(2 * len(regional_dr_dataset) * len(dld_dataset), len(graph.edges))

    def test_no_connection_between_dlds_and_drs_due_to_temporal_constraints(self):
        regional_dr_dataset = self.dr_dataset_local_region_1_morning
        graph = OperationalGraph()
        graph.add_delivery_requests(regional_dr_dataset)
        dld_dataset = create_loading_dock_afternoon_distribution()
        add_fully_connected_loading_docks(graph, dld_dataset)
        self.assertEqual(len(regional_dr_dataset) + len(dld_dataset), len(graph.nodes))
        self.assertEqual(0, len(graph.edges))

    def test_delivery_request_graph_creation(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_morning)
        drg.add_delivery_requests(self.dr_dataset_afternoon)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        self.assertEqual(_get_dr_from_dr_graph(drg), list(self.dr_dataset_morning) + list(self.dr_dataset_afternoon)
                         + list(self.dld_dataset_random))

    def test_graph_creation_with_edges(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_morning)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        edges = []
        for dk in self.dld_dataset_random:
            for dl in self.dr_dataset_morning:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttribs(Random().choice(range(10)))))
        drg.add_operational_edges(edges)
        returned_edges = list(drg.edges)
        self.assertEqual(len(drg.edges), len(edges))
        self.assertEqual(returned_edges[0].start_node, edges[0].start_node)
        self.assertEqual(returned_edges[0].end_node, edges[0].end_node)
        self.assertEqual(returned_edges[5].start_node, edges[5].start_node)
        self.assertEqual(returned_edges[5].end_node, edges[5].end_node)
        self.assertEqual(returned_edges[6].start_node, edges[6].start_node)
        self.assertEqual(returned_edges[6].end_node, edges[6].end_node)

    def test_drone_loading_dock_set_internal_graph(self):
        drg1 = OperationalGraph()
        drg1.add_drone_loading_docks(self.dld_dataset_random)
        drg2 = OperationalGraph()
        drg2.set_internal_graph(drg1._internal_graph)
        self.assertFalse(drg1.is_empty())
        self.assertEqual(_get_dr_from_dr_graph(drg1), _get_dr_from_dr_graph(drg2))

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

    def test_sub_graph_within_polygon(self):
        region_dataset = self.dr_dataset_local_region_1_morning + self.dr_dataset_local_region_2_morning
        graph = OperationalGraph()
        add_locally_connected_dr_graph(graph, region_dataset, max_cost_to_connect=self.radius_surrounding_region_1)
        region_1_polygon = create_polygon_2d([create_point_2d(100, 50), create_point_2d(100, 150),
                                              create_point_2d(200, 150), create_point_2d(200, 50)])
        subgraph_in_region_1 = graph.calc_subgraph_within_polygon(region_1_polygon)
        num_nodes_in_region_1_subgraph = len(subgraph_in_region_1.nodes)
        num_nodes_in_all_regions = len(region_dataset)
        expected_nodes_in_region_1 = num_nodes_in_all_regions / 2
        self.assertEqual(expected_nodes_in_region_1, num_nodes_in_region_1_subgraph)
        self.assertEqual(expected_nodes_in_region_1 * (expected_nodes_in_region_1 - 1), len(subgraph_in_region_1.edges))


def create_local_data_in_region_1_morning() -> [DeliveryRequest]:
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                delivery_request_distribution=(
                                                    _create_region_1_morning_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def create_local_data_in_region_2_morning() -> [DeliveryRequest]:
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                delivery_request_distribution=(
                                                    _create_region_2_morning_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def create_loading_dock_afternoon_distribution() -> [DroneLoadingDock]:
    return _create_loading_dock_afternoon_distribution().choose_rand(random=Random(42), amount=10)


def create_local_data_in_region_2_afternoon() -> [DeliveryRequest]:
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                delivery_request_distribution=(
                                                    _create_region_2_afternoon_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def create_morning_dr_dataset() -> [DeliveryRequest]:
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                delivery_request_distribution=(_create_morning_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def create_afternoon_dr_dataset() -> [DeliveryRequest]:
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=5,
                                                delivery_request_distribution=(_create_afternoon_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def create_top_priority_dr_dataset() -> [DeliveryRequest]:
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=4,
                                                delivery_request_distribution=(_create_high_priority_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def create_low_priority_dr_dataset() -> [DeliveryRequest]:
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=6,
                                                delivery_request_distribution=(_create_low_priority_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def _create_morning_dr_distribution() -> DeliveryRequestDistribution:
    return build_delivery_request_distribution(
        time_window_distribution=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(6, 0, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3, minutes=30))])))


def _create_afternoon_dr_distribution() -> DeliveryRequestDistribution:
    return build_delivery_request_distribution(
        time_window_distribution=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(16, 30, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=1, minutes=30))])))


def _create_high_priority_dr_distribution() -> DeliveryRequestDistribution:
    return build_delivery_request_distribution(priority_distribution=PriorityDistribution([101, 102, 103, 104, 105]))


def _create_low_priority_dr_distribution() -> DeliveryRequestDistribution:
    return build_delivery_request_distribution(priority_distribution=PriorityDistribution([1, 2, 3, 4, 5]))


def _get_dr_from_dr_graph(drg1) -> [DeliveryRequest]:
    return [n.internal_node for n in drg1.nodes]


def _create_region_1_morning_dr_distribution() -> DeliveryRequestDistribution:
    return build_delivery_request_distribution(
        relative_pdp_location_distribution=UniformPointInBboxDistribution(min_x=100, max_x=200, min_y=50, max_y=150),
        time_window_distribution=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(6, 0, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3, minutes=30))])))


def _create_region_2_morning_dr_distribution() -> DeliveryRequestDistribution:
    return build_delivery_request_distribution(
        relative_pdp_location_distribution=UniformPointInBboxDistribution(min_x=1100, max_x=1200, min_y=150, max_y=1150),
        time_window_distribution=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(6, 0, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3, minutes=30))])))


def _create_region_2_afternoon_dr_distribution() -> DeliveryRequestDistribution:
    return build_delivery_request_distribution(
        relative_pdp_location_distribution=UniformPointInBboxDistribution(min_x=1100, max_x=1200, min_y=150, max_y=1150),
        time_window_distribution=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(16, 30, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=1, minutes=30))])))


def _create_loading_dock_afternoon_distribution() -> DroneLoadingDockDistribution:
    return DroneLoadingDockDistribution(
        time_window_distributions=TimeWindowDistribution(
            start_time_distribution=DateTimeDistribution([DateTimeExtension(date(2021, 1, 1), time(16, 30, 0))]),
            time_delta_distribution=TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=1, minutes=30))])))
