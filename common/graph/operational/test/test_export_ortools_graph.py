import unittest
from datetime import time, date, timedelta
from random import Random

from common.entities.delivery_request import DeliveryRequestDistribution, generate_dr_distribution, PriorityDistribution
from common.entities.delivery_request_generator import DeliveryRequestDatasetGenerator, DeliveryRequestDatasetStructure
from common.entities.package import PackageType
from common.entities.temporal import TimeWindowDistribution, DateTimeDistribution, DateTimeExtension, \
    TimeDeltaExtension, TimeDeltaDistribution, TimeWindowExtension
from common.graph.operational.delivery_request_graph import OperationalGraph, OperationalEdge, OperationalNode, \
    OperationalEdgeAttributes
from common.entities.drone_loading_dock import DroneLoadingDockDistribution
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter


class BasicOrtoolsExporterTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_random = DeliveryRequestDistribution().choose_rand(Random(100), 10)
        cls.dld_dataset_random = DroneLoadingDockDistribution().choose_rand(Random(100), 3)
        cls.graph_exporter = OrtoolsGraphExporter()

    def test_export_time_window(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_random)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        edges = []
        for dk in self.dld_dataset_random:
            for dl in self.dr_dataset_random:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttributes(Random().choice(range(10)))))
        drg.add_operational_edges(edges)
        tw = self.graph_exporter.export_time_windows(drg)
        self.assertEqual(len(drg.nodes), len(tw))

    def test_export_priorities(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_random)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        edges = []
        for dk in self.dld_dataset_random:
            for dl in self.dr_dataset_random:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttributes(Random().choice(range(10)))))
        drg.add_operational_edges(edges)
        pr = self.graph_exporter.export_priorities(drg)
        self.assertEqual(len(drg.edges), len(pr))

    def test_export_travel_times(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_random)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        edges = []
        for dk in self.dld_dataset_random:
            for dl in self.dr_dataset_random:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttributes(Random().choice(range(10)))))
        drg.add_operational_edges(edges)
        tt = self.graph_exporter.export_travel_times(drg)
        self.assertEqual(len(drg.edges), len(tt))

    def test_delivery_request_indices(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_random)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        edges = []
        for dk in self.dld_dataset_random:
            for dl in self.dr_dataset_random:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttributes(Random().choice(range(10)))))
        drg.add_operational_edges(edges)
        dr_indices = self.graph_exporter.export_delivery_request_nodes_indices(drg)
        self.assertEqual(len(self.dr_dataset_random), len(dr_indices))

    def test_drone_loading_docks_indices(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_random)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        edges = []
        for dk in self.dld_dataset_random:
            for dl in self.dr_dataset_random:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttributes(Random().choice(range(10)))))
        drg.add_operational_edges(edges)
        drd_indices = self.graph_exporter.export_basis_nodes_indices(drg)
        self.assertEqual(len(self.dld_dataset_random), len(drd_indices))

    def test_package_type_demands(self):
        drg = OperationalGraph()
        drg.add_delivery_requests(self.dr_dataset_random)
        drg.add_drone_loading_docks(self.dld_dataset_random)
        edges = []
        for dk in self.dld_dataset_random:
            for dl in self.dr_dataset_random:
                edges.append(OperationalEdge(OperationalNode(dk), OperationalNode(dl),
                                             OperationalEdgeAttributes(Random().choice(range(10)))))
        drg.add_operational_edges(edges)
        large_package_demands = self.graph_exporter.export_package_type_demands(drg, PackageType.LARGE)
        self.assertEqual(len(large_package_demands), len(self.dr_dataset_random))


def _get_dr_from_dr_graph(drg1):
    return [n.internal_node for n in drg1.nodes]
