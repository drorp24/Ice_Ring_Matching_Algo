import unittest
from datetime import time, date, timedelta
from random import Random

from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.drone_loading_station_distribution import \
    DroneLoadingStationDistribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    TimeWindowDistribution, DateTimeDistribution, ExactTimeWindowDistribution
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension, TimeWindowExtension
from end_to_end.distribution.supplier_category_distribution import SupplierCategoryDistribution
from end_to_end.minimum_end_to_end import *
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, \
    NormalPointDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d

ZERO_TIME = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(0, 0, 0))


class BasicDeliveryRequestGraphFilterTest(unittest.TestCase):
    drs_amount = 10

    @classmethod
    def setUpClass(cls):
        cls.docks_amount = 1

        cls.supplier_category = cls._create_supplier_category_distribution().choose_rand(
            random=Random(10),
            amount={
                DeliveryRequest: BasicDeliveryRequestGraphFilterTest.drs_amount,
                DroneLoadingDock: cls.docks_amount})

        cls.package_packages_dependent_graph = cls._create_package_dependent_graph_model(
            cls.supplier_category,
            edge_cost_factor=25.0,
            edge_travel_time_factor=25.0)

        cls.package_packages_and_time_dependent_graph = cls._create_package_and_time_dependent_graph_model(
            cls.supplier_category,
            edge_cost_factor=25.0,
            edge_travel_time_factor=25.0)

    def test_filter_by_packages(self):
        expected_nodes = BasicDeliveryRequestGraphFilterTest.drs_amount + self.docks_amount

        expected_dr_by_package_type = [sum([True for dr in self.supplier_category.delivery_requests if
                                            dr.delivery_options[0].customer_deliveries[0].package_delivery_plans[
                                                0].package_type == package_type]) for package_type in PackageType]

        expected_edges = sum(map(lambda i: i * (i - 1), expected_dr_by_package_type)) + 2 * len(
            self.supplier_category.delivery_requests)

        self.assertEqual(expected_nodes, len(self.package_packages_dependent_graph.nodes))
        self.assertEqual(expected_edges, len(self.package_packages_dependent_graph.edges))

    def test_filter_by_time_and_packages(self):
        expected_nodes = self.drs_amount + self.docks_amount
        expected_edges = self.drs_amount * 2

        expected_dr_by_package_type = [[dr for dr in self.supplier_category.delivery_requests if
                                            dr.delivery_options[0].customer_deliveries[0].package_delivery_plans[
                                                0].package_type == package_type] for package_type in PackageType]

        for drs in expected_dr_by_package_type:
            for selected_node_index, origin_node in enumerate(drs):
                destinations = list(filter(lambda x: x != origin_node
                                 and has_overlapping_time_window(origin_node,x),
                                drs[selected_node_index:]))

                expected_edges += len(destinations) * 2

        self.assertEqual(expected_nodes, len(self.package_packages_and_time_dependent_graph.nodes))
        self.assertEqual(expected_edges , len(self.package_packages_and_time_dependent_graph.edges))

    @staticmethod
    def _create_standard_full_day_test_time():
        return TimeWindowDistribution(DateTimeDistribution([ZERO_TIME]),
                                      TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=23, minutes=59))]))

    @staticmethod
    def _create_multi_package_distribution():
        package_type_distribution_dict = {PackageType.MEDIUM: 0.3, PackageType.LARGE: 0.7}
        package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
        return package_distribution

    @staticmethod
    def _create_exact_time_window_distribution():
        time_window_1 = TimeWindowExtension(
            since=ZERO_TIME,
            until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=30))))

        time_window_2 = TimeWindowExtension(
            since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(hours=1, minutes=0))),
            until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(hours=3, minutes=0))))

        time_dist = ExactTimeWindowDistribution([time_window_1] * (BasicDeliveryRequestGraphFilterTest.drs_amount - 2)+
                                                [time_window_2] * 2 )

        return time_dist

    @staticmethod
    def _create_delivery_request_distribution(center_point: Point2D, sigma_lon: float, sigma_lat: float,
                                              lowest_priority: int = 10) -> DeliveryRequestDistribution:
        delivery_request_distribution = build_delivery_request_distribution(
            package_type_distribution=BasicDeliveryRequestGraphFilterTest._create_multi_package_distribution(),
            relative_dr_location_distribution=NormalPointDistribution(center_point, sigma_lon, sigma_lat),
            priority_distribution=PriorityDistribution(list(range(1, lowest_priority))),
            time_window_distribution=BasicDeliveryRequestGraphFilterTest._create_exact_time_window_distribution())
        return delivery_request_distribution

    @staticmethod
    def _create_supplier_category_distribution():
        return SupplierCategoryDistribution(
            zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
            delivery_requests_distribution=BasicDeliveryRequestGraphFilterTest._create_delivery_request_distribution(
                create_point_2d(35.11, 32.0),
                0.03,
                0.05, 10),
            drone_loading_docks_distribution=DroneLoadingDockDistribution(
                drone_loading_station_distributions=DroneLoadingStationDistribution(
                    drone_station_locations_distribution=UniformPointInBboxDistribution(35.11,
                                                                                        35.11,
                                                                                        31.79, 31.79
                                                                                        )),
                time_window_distributions=BasicDeliveryRequestGraphFilterTest._create_standard_full_day_test_time()))

    @staticmethod
    def _create_package_dependent_graph_model(supplier_category: SupplierCategory,
                                              edge_cost_factor: float = 1.0,
                                              edge_travel_time_factor: float = 1.0) -> OperationalGraph:
        operational_graph = OperationalGraph()
        operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
        operational_graph.add_delivery_requests(supplier_category.delivery_requests)
        build_package_dependent_connected_graph(operational_graph, edge_cost_factor, edge_travel_time_factor)
        return operational_graph

    @staticmethod
    def _create_package_and_time_dependent_graph_model(supplier_category: SupplierCategory,
                                                       edge_cost_factor: float = 1.0,
                                                       edge_travel_time_factor: float = 1.0) -> OperationalGraph:
        operational_graph = OperationalGraph()
        operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
        operational_graph.add_delivery_requests(supplier_category.delivery_requests)
        build_package_and_time_dependent_connected_graph(operational_graph, edge_cost_factor, edge_travel_time_factor)
        return operational_graph
