import unittest
from datetime import time, date, timedelta, datetime
from pathlib import Path
from random import Random

from common.entities.base_entities.drone import PackageConfiguration, DroneType
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_zone_delivery_request_distribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.drone_loading_station_distribution import \
    DroneLoadingStationDistribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    TimeWindowDistribution, DateTimeDistribution
from common.entities.base_entities.entity_distribution.zone_delivery_request_distribution import \
    ZoneDeliveryRequestDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import build_empty_drone_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneFormationTypePolicy, \
    PackageConfigurationPolicy, DroneSetProperties
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension
from end_to_end.distribution.supplier_category_distribution import SupplierCategoryDistribution
from end_to_end.arrival_envelope_minimum_end_to_end import *
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, \
    NormalPointsInMultiPolygonDistribution
from geometry.geo_factory import create_point_2d, create_polygon_2d, create_multipolygon_2d
from matching.matcher_config import MatcherConfig
from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import create_drawer_2d, MapImage
from visualization.basic.pltgantt_drawer import create_gantt_drawer
from visualization.operational import operational_drawer2d
from visualization.operational import operational_gantt_drawer

ZERO_TIME = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(0, 0, 0))


class BasicMinimumEnd2EndClusteredDrsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        match_config_file_path = Path('end_to_end/tests/jsons/test_matcher_config.json')
        cls.match_config = MatcherConfig.dict_to_obj(MatcherConfig.json_to_dict(match_config_file_path))

        cls.mapImage = MapImage(map_background_path=Path(r"visualization/basic/gush_dan_background.Png"),
                                west_lon=34.83927, east_lon=35.32341, south_lat=31.77279, north_lat=32.19276)

    def test_1_zone_1_centroid(self):
        self._test_clustered_drs(zone_amount=1, max_centroids_per_zone=1, drs_amount=37, docks_amount=1,
                                 max_clusters_per_zone=5, dr_timewindow=18, draw_match=False)

    def test_1_zone_2_centroids(self):
        self._test_clustered_drs(zone_amount=1, max_centroids_per_zone=2, drs_amount=37, docks_amount=1,
                                 max_clusters_per_zone=5, dr_timewindow=18, draw_match=False)

    def test_1_zone_3_centroids(self):
        self._test_clustered_drs(zone_amount=1, max_centroids_per_zone=3, drs_amount=37, docks_amount=1,
                                 max_clusters_per_zone=5, dr_timewindow=18, draw_match=False)

    def test_2_zones_1_centroid(self):
        self._test_clustered_drs(zone_amount=2, max_centroids_per_zone=1, drs_amount=37, docks_amount=1,
                                 max_clusters_per_zone=3, dr_timewindow=23, draw_match=False)

    def test_2_zones_2_centroids(self):
        self._test_clustered_drs(zone_amount=2, max_centroids_per_zone=2, drs_amount=37, docks_amount=1,
                                 max_clusters_per_zone=3, dr_timewindow=18, draw_match=False)

    def test_2_zones_3_centroids(self):
        self._test_clustered_drs(zone_amount=2, max_centroids_per_zone=3, drs_amount=37, docks_amount=1,
                                 max_clusters_per_zone=3, dr_timewindow=18, draw_match=False)

    def _test_clustered_drs(self, zone_amount: int = 1, max_centroids_per_zone: int = 1, drs_amount: int = 10,
                            docks_amount: int = 1, max_clusters_per_zone: int = 1, dr_timewindow: int = 3,
                            draw_match: bool = False, drone_deliveries_amount=20):
        print("--- _test_clustered_drs time: %s  ---" % datetime.now())
        start_time = datetime.now()

        supplier_category = _create_supplier_category_distribution(
            zone_amount=zone_amount,
            max_centroids_per_polygon=max_centroids_per_zone,
            sigma_lon=0.03, sigma_lat=0.02,
            dr_timewindow=dr_timewindow).choose_rand(
            random=Random(10),
            amount={
                DeliveryRequest: drs_amount,
                DroneLoadingDock: docks_amount})

        clustered_connected_graph = create_clustered_delivery_requests_graph_model(supplier_category,
                                                                                   edge_cost_factor=0.1,
                                                                                   edge_travel_time_factor=0.1,
                                                                                   max_clusters_per_zone=max_clusters_per_zone)

        print("--- clustered_connected_graph run time: %s  ---" % (datetime.now() - start_time))
        start_time = datetime.now()

        expected_delivery_requests_clusters = list(itertools.chain.from_iterable((
            map(lambda item: list(
                split_delivery_requests_into_clusters(delivery_requests=item[1],
                                                      max_clusters=max_clusters_per_zone).values()),
                sort_delivery_requests_by_zone(supplier_category.delivery_requests, supplier_category.zones).items()))))

        expected_num_edge_in_graph = sum(
            [len(drs) * (len(drs) - 1) for drs in expected_delivery_requests_clusters]) + (
                                                   2 * len(supplier_category.delivery_requests))

        print("#expected delivery requests clusters", len(expected_delivery_requests_clusters))
        self.assertLessEqual(len(expected_delivery_requests_clusters), max_clusters_per_zone * zone_amount)
        self.assertEqual((drs_amount + docks_amount), len(clustered_connected_graph.nodes))
        self.assertEqual(expected_num_edge_in_graph, len(clustered_connected_graph.edges))

        print("--- assert expected values run time: %s  ---" % (datetime.now() - start_time))

        delivery_board = self._run_match(clustered_connected_graph, drone_deliveries_amount)
        # print(delivery_board)

        if draw_match:
            self._draw_matched_supplier_category(clustered_connected_graph, delivery_board, supplier_category,
                                                 self.mapImage)

    def _draw_matched_supplier_category(self, clustered_connected_graph, delivery_board, supplier_category, map_image):
        dr_drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC, map_image)
        operational_drawer2d.add_operational_graph(dr_drawer, clustered_connected_graph, draw_internal=True,
                                                   draw_edges=False)
        dr_drawer.draw(False)
        board_map_drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC, map_image)
        operational_drawer2d.add_delivery_board(board_map_drawer, delivery_board, draw_unmatched=True)
        board_map_drawer.draw(False)
        row_names = ["Unmatched Out"] + \
                    ["[" + str(delivery.drone_formation.drone_formation_type.name) + "] * " +
                     str(delivery.drone_formation.drone_package_configuration.package_type_map)
                     for delivery in delivery_board.drone_deliveries]
        board_gantt_drawer = create_gantt_drawer(zero_time=supplier_category.zero_time,
                                                 hours_period=24,
                                                 row_names=row_names,
                                                 rows_title='Formation Type x Package Type Amounts'
                                                 )
        operational_gantt_drawer.add_delivery_board(board_gantt_drawer, delivery_board, True)
        board_gantt_drawer.draw(True)

    def _run_match(self, clustered_connected_graph, drone_deliveries_amount) -> DroneDeliveryBoard:
        empty_drone_delivery_board = _create_empty_drone_delivery_board(amount=drone_deliveries_amount,
                                                                        max_route_time_entire_board=45,
                                                                        velocity_entire_board=10.0)

        matcher_input = MatcherInput(graph=clustered_connected_graph, empty_board=empty_drone_delivery_board,
                                     config=self.match_config)
        start_time = datetime.now()

        delivery_board = calc_assignment(matcher_input=matcher_input)

        print("--- calc_assignment run time: %s  ---" % (datetime.now() - start_time))

        return delivery_board


def _create_standard_full_day_test_time():
    return TimeWindowDistribution(DateTimeDistribution([ZERO_TIME]),
                                  TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=23, minutes=59))]))


def _create_zones(zone_amount: int = 1) -> List[Zone]:
    return [
               Zone(create_polygon_2d([create_point_2d(35.03, 31.82),
                                       create_point_2d(35.03, 32.01),
                                       create_point_2d(35.3, 32.01),
                                       create_point_2d(35.3, 31.82)]), id=EntityID.generate_uuid()),
               Zone(create_polygon_2d([create_point_2d(35.03, 32.01),
                                       create_point_2d(35.09, 32.18),
                                       create_point_2d(35.3, 32.18),
                                       create_point_2d(35.3, 32.01)]), id=EntityID.generate_uuid())
           ][0:zone_amount]


def _create_zone_delivery_request_distribution(sigma_lon: float, sigma_lat: float,
                                               lowest_priority: int = 10,
                                               dr_timewindow: int = 3,
                                               max_centroids_per_polygon: int = 1,
                                               zone_amount: int = 1) -> ZoneDeliveryRequestDistribution:
    package_distribution = _create_single_package_distribution()
    zero_time = ZERO_TIME
    time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=dr_timewindow, minutes=0))])
    dt_options = [zero_time.add_time_delta(TimeDeltaExtension(timedelta(hours=x))) for x in range(24 - dr_timewindow)]

    time_window_distribution = TimeWindowDistribution(DateTimeDistribution(dt_options), time_delta_distrib)

    zones = _create_zones(zone_amount)
    zones_regions = create_multipolygon_2d([zone.region for zone in zones])
    zone_delivery_request_distribution = build_zone_delivery_request_distribution(
        zones=zones,
        package_type_distribution=package_distribution,
        relative_dr_location_distribution=NormalPointsInMultiPolygonDistribution(
            multi_polygon=zones_regions,
            max_centroids_per_polygon=max_centroids_per_polygon,
            sigma_x=sigma_lon, sigma_y=sigma_lat),
        priority_distribution=PriorityDistribution(list(range(1, lowest_priority))),
        time_window_distribution=time_window_distribution)
    return zone_delivery_request_distribution


def _create_single_package_distribution():
    package_type_distribution_dict = {PackageType.LARGE: 1}
    package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
    return package_distribution


def _create_empty_drone_delivery_board(
        drone_formation_policy=DroneFormationTypePolicy({DroneFormationType.PAIR: 1, DroneFormationType.QUAD: 0}),
        package_configurations_policy=PackageConfigurationPolicy({PackageConfiguration.LARGE_X2: 0.9,
                                                                  PackageConfiguration.MEDIUM_X4: 0.1,
                                                                  PackageConfiguration.SMALL_X8: 0,
                                                                  PackageConfiguration.TINY_X16: 0}),
        drone_type: DroneType = DroneType.drone_type_1,
        amount: int = 30, max_route_time_entire_board: int = 400, velocity_entire_board: float = 10.0):
    drone_set_properties = DroneSetProperties(drone_type=drone_type,
                                              package_configuration_policy=package_configurations_policy,
                                              drone_formation_policy=drone_formation_policy,
                                              drone_amount=amount)
    return build_empty_drone_delivery_board(drone_set_properties, max_route_time_entire_board,
                                            velocity_entire_board)


def _create_supplier_category_distribution(zone_amount: int = 1, max_centroids_per_polygon: int = 1,
                                           sigma_lon: float = 1,
                                           sigma_lat: float = 1,
                                           dr_timewindow: int = 3):
    return SupplierCategoryDistribution(
        zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
        delivery_requests_distribution=_create_zone_delivery_request_distribution(
            sigma_lon=sigma_lon,
            sigma_lat=sigma_lat,
            lowest_priority=10,
            dr_timewindow=dr_timewindow,
            max_centroids_per_polygon=max_centroids_per_polygon,
            zone_amount=zone_amount),
        drone_loading_docks_distribution=DroneLoadingDockDistribution(
            drone_loading_station_distributions=DroneLoadingStationDistribution(
                drone_station_locations_distribution=UniformPointInBboxDistribution(35.11,
                                                                                    35.11,
                                                                                    31.79, 31.79
                                                                                    )),
            time_window_distributions=_create_standard_full_day_test_time()))
