import unittest
from datetime import date, time
from random import Random

from common.entities.delivery_request import DeliveryRequestDistribution
from common.entities.package import PackageType
from common.entities.temporal import DateTimeExtension
from common.graph.operational.operational_graph import OperationalGraph, OperationalEdge, OperationalNode, \
    OperationalEdgeAttribs
from common.entities.drone_loading_dock import DroneLoadingDockDistribution
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter


class BasicOrtoolsExporterTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(Random(100), 10)
        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(Random(100), 3)
        cls.edges = cls.generate_edges()
        cls.graph_exporter = OrtoolsGraphExporter()
        cls.operational_graph = OperationalGraph()
        cls.operational_graph.add_delivery_requests(cls.dr_dataset_random)
        cls.operational_graph.add_drone_loading_docks(cls.dld_dataset_random)
        cls.operational_graph.add_operational_edges(cls.edges)

    @classmethod
    def generate_edges(cls):
        edges = []
        for dk in cls.dld_dataset_random:
            for dl in cls.dr_dataset_random:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttribs(Random().choice(range(10)))))
        return edges

    def test_export_time_window(self):
        zero_time = DateTimeExtension(dt_date=date(2021, 1, 1),dt_time=time(0, 0, 0))
        time_windows = self.graph_exporter.export_time_windows(self.operational_graph,zero_time)

        self.assertEqual(len(self.operational_graph.nodes), len(time_windows))
        self.assertEqual(time_windows[0], self.dr_dataset_random[0].time_window.get_relative_time_in_min(zero_time))
        self.assertEqual(time_windows[1], self.dr_dataset_random[1].time_window.get_relative_time_in_min(zero_time))
        self.assertEqual(time_windows[4], self.dr_dataset_random[4].time_window.get_relative_time_in_min(zero_time))
        self.assertEqual(time_windows[6], self.dr_dataset_random[6].time_window.get_relative_time_in_min(zero_time))
        self.assertEqual(time_windows[9], self.dr_dataset_random[9].time_window.get_relative_time_in_min(zero_time))
        self.assertEqual(time_windows[10], self.dld_dataset_random[0].time_window.get_relative_time_in_min(zero_time))
        self.assertEqual(time_windows[11], self.dld_dataset_random[1].time_window.get_relative_time_in_min(zero_time))
        self.assertEqual(time_windows[12], self.dld_dataset_random[2].time_window.get_relative_time_in_min(zero_time))

    def test_export_priorities(self):
        priorities = self.graph_exporter.export_priorities(self.operational_graph)
        self.assertEqual(len(self.operational_graph.nodes), len(priorities))
        self.assertEqual(priorities[0], self.dr_dataset_random[0].priority)
        self.assertEqual(priorities[1], self.dr_dataset_random[1].priority)
        self.assertEqual(priorities[4], self.dr_dataset_random[4].priority)
        self.assertEqual(priorities[6], self.dr_dataset_random[6].priority)
        self.assertEqual(priorities[9], self.dr_dataset_random[9].priority)
        self.assertEqual(priorities[10], self.dld_dataset_random[0].priority)
        self.assertEqual(priorities[11], self.dld_dataset_random[1].priority)
        self.assertEqual(priorities[12], self.dld_dataset_random[2].priority)

    def test_export_travel_times(self):
        travel_times = self.graph_exporter.export_travel_times(self.operational_graph)
        nodes = list(self.operational_graph.nodes)
        for edge in self.edges:
            start_node_index = nodes.index(edge.start_node)
            end_node_index = nodes.index(edge.end_node)
            self.assertEqual(travel_times[start_node_index][end_node_index], edge.attributes.cost)

    def test_delivery_request_indices(self):
        dr_indices = self.graph_exporter.export_delivery_request_nodes_indices(self.operational_graph)
        self.assertEqual(len(self.dr_dataset_random), len(dr_indices))
        self.assertEqual(dr_indices, list(range(10)))

    def test_drone_loading_docks_indices(self):
        drd_indices = self.graph_exporter.export_basis_nodes_indices(self.operational_graph)
        self.assertEqual(len(self.dld_dataset_random), len(drd_indices))
        self.assertEqual(drd_indices, list(range(10, 13)))

    def test_package_type_demands(self):
        large_package_demands = self.graph_exporter.export_package_type_demands(self.operational_graph,
                                                                                PackageType.LARGE)
        self.assertEqual(len(large_package_demands), len(self.dr_dataset_random) + len(self.dld_dataset_random))
