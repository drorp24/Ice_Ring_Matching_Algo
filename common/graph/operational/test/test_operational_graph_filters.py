import unittest
from datetime import time, date, timedelta
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution, build_zone_delivery_request_distribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.drone_loading_station_distribution import \
    DroneLoadingStationDistribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    TimeWindowDistribution, DateTimeDistribution, ExactTimeWindowDistribution
from common.entities.base_entities.entity_distribution.zone_delivery_request_distribution import \
    ZoneDeliveryRequestDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension, TimeWindowExtension
from common.graph.operational.arrival_envelope_graph_creator import build_package_dependent_connected_graph
from common.graph.operational.graph_creator import build_package_and_time_dependent_connected_graph
from common.graph.operational.graph_utils import has_overlapping_time_window
from common.graph.operational.operational_graph import OperationalGraph
from experiment_space.distribution.supplier_category_distribution import SupplierCategoryDistribution
from experiment_space.supplier_category import SupplierCategory
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, \
    NormalPointDistribution, NormalPointsInMultiPolygonDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d, create_polygon_2d, create_multipolygon_2d
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.operational.operational_drawer2d import add_operational_graph

ZERO_TIME = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(0, 0, 0))


class BasicDeliveryRequestGraphFilterTest(unittest.TestCase):
    drs_amount = 50

    @classmethod
    def setUpClass(cls):
        cls.docks_amount = 1
        cls.draw_graph = False

        cls.supplier_category = cls.create_supplier_category_distribution(
            zone_amount=3,
            max_centroids_per_polygon=3,
            sigma_lon=0.01, sigma_lat=0.01,
            dr_timewindow=18).choose_rand(
            random=Random(10),
            amount={
                DeliveryRequest: BasicDeliveryRequestGraphFilterTest.drs_amount,
                DroneLoadingDock: cls.docks_amount})[0]

        cls.packages_dependent_graph = cls.create_package_dependent_graph_model(
            cls.supplier_category,
            edge_cost_factor=25.0,
            edge_travel_time_factor=25.0)

        cls.packages_time_dependent_graph = cls.create_package_time_dependent_graph_model(
            cls.supplier_category,
            edge_cost_factor=25.0,
            edge_travel_time_factor=25.0)

        cls.packages_time_zones_dependent_graph = cls.create_package_time_zones_dependent_graph_model(
            cls.supplier_category,
            edge_cost_factor=25.0,
            edge_travel_time_factor=25.0)

        if cls.draw_graph:
            cls.draw_zone_graph(cls.packages_time_zones_dependent_graph)

    def test_filter_by_packages(self):
        expected_nodes = BasicDeliveryRequestGraphFilterTest.drs_amount + self.docks_amount

        expected_dr_by_package_type = [sum([True for dr in self.supplier_category.delivery_requests if
                                            dr.delivery_options[0].customer_deliveries[0].package_delivery_plans[
                                                0].package_type == package_type]) for package_type in PackageType]

        expected_edges = sum(map(lambda i: i * (i - 1), expected_dr_by_package_type)) + 2 * len(
            self.supplier_category.delivery_requests)

        self.assertEqual(expected_nodes, len(self.packages_dependent_graph.nodes))
        self.assertEqual(expected_edges, len(self.packages_dependent_graph.edges))

    def test_filter_by_packages_time(self):
        expected_nodes = self.drs_amount + self.docks_amount
        expected_edges = self.drs_amount * 2

        expected_dr_by_package_type = [[dr for dr in self.supplier_category.delivery_requests if
                                        dr.delivery_options[0].customer_deliveries[0].package_delivery_plans[
                                            0].package_type == package_type] for package_type in PackageType]

        for drs in expected_dr_by_package_type:
            for selected_node_index, origin_node in enumerate(drs):
                destinations = list(filter(lambda x: x != origin_node
                                                     and has_overlapping_time_window(origin_node, x),
                                           drs[selected_node_index:]))

                expected_edges += len(destinations) * 2

        self.assertEqual(expected_nodes, len(self.packages_time_dependent_graph.nodes))
        self.assertEqual(expected_edges, len(self.packages_time_dependent_graph.edges))

    def test_filter_by_packages_time_zones(self):

        expected_nodes = self.drs_amount + self.docks_amount
        expected_edges = self.drs_amount * 2

        delivery_requests_by_zone = sort_delivery_requests_by_zone(self.supplier_category.delivery_requests,
                                                                   BasicDeliveryRequestGraphFilterTest.create_zones(
                                                                       zone_amount=3))

        for drs_zones in delivery_requests_by_zone.values():
            expected_dr_by_package_type = [[dr for dr in drs_zones if
                                            dr.delivery_options[0].customer_deliveries[0].package_delivery_plans[
                                                0].package_type == package_type] for package_type in PackageType]

            for drs_pt in expected_dr_by_package_type:
                for selected_node_index, origin_node in enumerate(drs_pt):
                    destinations = list(filter(lambda x: x != origin_node
                                                         and has_overlapping_time_window(origin_node, x),
                                               drs_pt[selected_node_index:]))

                    expected_edges += len(destinations) * 2

        self.assertEqual(expected_nodes, len(self.packages_time_zones_dependent_graph.nodes))
        self.assertEqual(expected_edges, len(self.packages_time_zones_dependent_graph.edges))

    @staticmethod
    def draw_zone_graph(og):
        d = create_drawer_2d()
        add_operational_graph(d, og, radius=0.01)
        d.draw()

    @staticmethod
    def create_standard_full_day_test_time()->TimeWindowDistribution:
        return TimeWindowDistribution(DateTimeDistribution([ZERO_TIME]),
                                      TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=23, minutes=59))]))

    @staticmethod
    def create_multi_package_distribution()->PackageDistribution:
        package_type_distribution_dict = {PackageType.MEDIUM: 0.3, PackageType.LARGE: 0.7}
        package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
        return package_distribution

    @staticmethod
    def create_exact_time_window_distribution()->ExactTimeWindowDistribution:
        time_window_1 = TimeWindowExtension(
            since=ZERO_TIME,
            until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=30))))

        time_window_2 = TimeWindowExtension(
            since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(hours=1, minutes=0))),
            until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(hours=3, minutes=0))))

        time_dist = ExactTimeWindowDistribution([time_window_1] * (BasicDeliveryRequestGraphFilterTest.drs_amount - 2) +
                                                [time_window_2] * 2)

        return time_dist

    @staticmethod
    def create_delivery_request_distribution(center_point: Point2D, sigma_lon: float, sigma_lat: float,
                                             lowest_priority: int = 10) -> DeliveryRequestDistribution:
        delivery_request_distribution = build_delivery_request_distribution(
            package_type_distribution=BasicDeliveryRequestGraphFilterTest.create_multi_package_distribution(),
            relative_dr_location_distribution=NormalPointDistribution(center_point, sigma_lon, sigma_lat),
            priority_distribution=PriorityDistribution(list(range(1, lowest_priority))),
            time_window_distribution=BasicDeliveryRequestGraphFilterTest.create_exact_time_window_distribution())
        return delivery_request_distribution

    @staticmethod
    def create_zones(zone_amount: int = 1) -> List[Zone]:
        return [
                   Zone(create_polygon_2d([create_point_2d(35.03, 31.82),
                                           create_point_2d(35.03, 32.01),
                                           create_point_2d(35.3, 32.01),
                                           create_point_2d(35.3, 31.82)]), id=EntityID.generate_uuid()),
                   Zone(create_polygon_2d([create_point_2d(35.03, 32.01),
                                           create_point_2d(35.03, 32.18),
                                           create_point_2d(35.3, 32.18),
                                           create_point_2d(35.3, 32.01)]), id=EntityID.generate_uuid()),
                   Zone(create_polygon_2d([create_point_2d(35.03, 32.18),
                                           create_point_2d(35.03, 32.28),
                                           create_point_2d(35.3, 32.18),
                                           create_point_2d(35.3, 32.28)]), id=EntityID.generate_uuid())
               ][0:zone_amount]

    @staticmethod
    def create_zone_delivery_request_distribution(sigma_lon: float, sigma_lat: float,
                                                  lowest_priority: int = 10,
                                                  dr_timewindow: int = 3,
                                                  max_centroids_per_polygon: int = 1,
                                                  zone_amount: int = 1) -> ZoneDeliveryRequestDistribution:

        zero_time = ZERO_TIME
        time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=dr_timewindow, minutes=0))])
        dt_options = [zero_time.add_time_delta(TimeDeltaExtension(timedelta(hours=x))) for x in
                      range(24 - dr_timewindow)]

        time_window_distribution = TimeWindowDistribution(DateTimeDistribution(dt_options), time_delta_distrib)

        zones = BasicDeliveryRequestGraphFilterTest.create_zones(zone_amount)
        zones_regions = create_multipolygon_2d([zone.region for zone in zones])
        zone_delivery_request_distribution = build_zone_delivery_request_distribution(
            zones=zones,
            package_type_distribution=BasicDeliveryRequestGraphFilterTest.create_multi_package_distribution(),
            relative_dr_location_distribution=NormalPointsInMultiPolygonDistribution(
                multi_polygon=zones_regions,
                max_centroids_per_polygon=max_centroids_per_polygon,
                sigma_x=sigma_lon, sigma_y=sigma_lat),
            priority_distribution=PriorityDistribution(list(range(1, lowest_priority))),
            time_window_distribution=time_window_distribution)
        return zone_delivery_request_distribution

    @staticmethod
    def create_supplier_category_distribution(zone_amount: int = 1, max_centroids_per_polygon: int = 1,
                                              sigma_lon: float = 1,
                                              sigma_lat: float = 1,
                                              dr_timewindow: int = 3)->SupplierCategoryDistribution:
        return SupplierCategoryDistribution(
            zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
            delivery_requests_distribution=
            BasicDeliveryRequestGraphFilterTest.create_zone_delivery_request_distribution(
                sigma_lon=sigma_lon,
                sigma_lat=sigma_lat,
                lowest_priority=10,
                dr_timewindow=dr_timewindow,
                max_centroids_per_polygon=max_centroids_per_polygon,
                zone_amount=zone_amount),
            drone_loading_docks_distribution=DroneLoadingDockDistribution(
                drone_loading_station_distributions=DroneLoadingStationDistribution(
                    drone_station_locations_distribution=UniformPointInBboxDistribution(35.33,
                                                                                        35.33,
                                                                                        32.12, 32.12
                                                                                        )),
                time_window_distributions=BasicDeliveryRequestGraphFilterTest.create_standard_full_day_test_time()))

    @staticmethod
    def create_package_dependent_graph_model(supplier_category: SupplierCategory,
                                             edge_cost_factor: float = 1.0,
                                             edge_travel_time_factor: float = 1.0) -> OperationalGraph:
        operational_graph = OperationalGraph()
        operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
        operational_graph.add_delivery_requests(supplier_category.delivery_requests)
        build_package_dependent_connected_graph(operational_graph, edge_cost_factor, edge_travel_time_factor)
        return operational_graph

    @staticmethod
    def create_package_time_dependent_graph_model(supplier_category: SupplierCategory,
                                                  edge_cost_factor: float = 1.0,
                                                  edge_travel_time_factor: float = 1.0) -> OperationalGraph:
        operational_graph = OperationalGraph()
        operational_graph.add_drone_loading_docks(supplier_category.drone_loading_docks)
        operational_graph.add_delivery_requests(supplier_category.delivery_requests)
        build_package_time_dependent_connected_graph(operational_graph, edge_cost_factor, edge_travel_time_factor)
        return operational_graph

    @staticmethod
    def create_package_time_zones_dependent_graph_model(supplier_category: SupplierCategory,
                                                        edge_cost_factor: float = 1.0,
                                                        edge_travel_time_factor: float = 1.0) -> OperationalGraph:

        return create_package_time_zones_dependent_graph_model(delivery_requests=supplier_category.delivery_requests,
                                                               drone_loading_docks=supplier_category.drone_loading_docks,
                                                               zones=supplier_category.zones,
                                                               edge_cost_factor=edge_cost_factor,
                                                               edge_travel_time_factor=edge_travel_time_factor)
