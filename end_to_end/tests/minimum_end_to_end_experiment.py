from datetime import time, date, timedelta, datetime
from pathlib import Path
from random import Random

from common.entities.base_entities.drone import PackageConfiguration, DroneType
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.drone_loading_station_distribution import \
    DroneLoadingStationDistribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeDeltaDistribution, \
    TimeWindowDistribution, DateTimeDistribution
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import build_empty_drone_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneFormationTypePolicy, \
    PackageConfigurationPolicy, DroneSetProperties
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import DateTimeExtension, TimeDeltaExtension
from end_to_end.distribution.supplier_category_distribution import SupplierCategoryDistribution
from end_to_end.minimum_end_to_end import *
from geometry.distribution.geo_distribution import NormalPointDistribution, UniformPointInBboxDistribution
from geometry.geo_factory import create_point_2d
from geometry.geo2d import Point2D
from matching.matcher_config import MatcherConfig
from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import create_drawer_2d, MapImage
from visualization.basic.pltgantt_drawer import create_gantt_drawer
from visualization.operational import operational_drawer2d
from visualization.operational import operational_gantt_drawer

west_lon = 34.83927
east_lon = 35.32341
south_lat = 31.77279
north_lat = 32.19276

ZERO_TIME = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(0, 0, 0))


def create_standard_full_day_test_time():
    default_start = ZERO_TIME
    default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=23, minutes=59))])
    default_dt_options = [default_start]
    return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)


def _create_delivery_request_distribution(center_point: Point2D, sigma_lon: float, sigma_lat: float,
                                          lowest_priority: int = 10, dr_timewindow: int = 3):
    package_distribution = create_single_package_distribution()
    zero_time = ZERO_TIME
    time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=dr_timewindow, minutes=0))])
    dt_options = [zero_time.add_time_delta(TimeDeltaExtension(timedelta(hours=x))) for x in range(24 - dr_timewindow)]

    time_window_distribution = TimeWindowDistribution(DateTimeDistribution(dt_options), time_delta_distrib)

    delivery_request_distribution = build_delivery_request_distribution(
        package_type_distribution=package_distribution,
        relative_dr_location_distribution=NormalPointDistribution(center_point, sigma_lon, sigma_lat),
        priority_distribution=PriorityDistribution(list(range(1, lowest_priority))),
        time_window_distribution=time_window_distribution)
    return delivery_request_distribution


def create_single_package_distribution():
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
    return build_empty_drone_delivery_board(drone_set_properties, max_route_time_entire_board, velocity_entire_board)


class BasicMinimumEnd2EndExperiment:

    def __init__(self, scene: str):
        self.matcher_config = Path("end_to_end/tests/jsons/test_matcher_config.json")
        if scene == 'north':
            self.supplier_category_distribution = SupplierCategoryDistribution(
                zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
                delivery_requests_distribution=_create_delivery_request_distribution(
                    create_point_2d(35.45, 33.4 - 0.5 * 1), 0.05, 0.06, 10, 3),
                drone_loading_docks_distribution=DroneLoadingDockDistribution(
                    drone_loading_station_distributions=DroneLoadingStationDistribution(
                        drone_station_locations_distribution=UniformPointInBboxDistribution(35.19336,
                                                                                            35.19336,
                                                                                            32.6675,
                                                                                            32.6675
                                                                                            )),
                    time_window_distributions=create_standard_full_day_test_time()))
            self.mapImage = MapImage(map_background_path=Path("visualization/basic/North_map.png"),
                                     west_lon=34.90777, east_lon=35.90753, south_lat=32.48928, north_lat=33.93233)
        elif scene == 'center':
            self.supplier_category_distribution = SupplierCategoryDistribution(
                zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
                delivery_requests_distribution=_create_delivery_request_distribution(create_point_2d(35.11, 32.0), 0.03,
                                                                                     0.05, 10, 3),
                drone_loading_docks_distribution=DroneLoadingDockDistribution(
                    drone_loading_station_distributions=DroneLoadingStationDistribution(
                        drone_station_locations_distribution=UniformPointInBboxDistribution(35.11,
                                                                                            35.11,
                                                                                            31.79, 31.79
                                                                                            )),
                    time_window_distributions=create_standard_full_day_test_time()))
            self.matcher_config = Path("end_to_end/tests/jsons/test_matcher_config.json")
            self.mapImage = MapImage(map_background_path=Path("visualization/basic/gush_dan_background.Png"),
                                     west_lon=34.83927, east_lon=35.32341, south_lat=31.77279, north_lat=32.19276)

    def test_small_supplier_category(self):
        start_time = datetime.now()
        empty_drone_delivery_board = _create_empty_drone_delivery_board(amount=80, max_route_time_entire_board=45,
                                                                        velocity_entire_board=10.0)
        print("--- _create_empty_drone_delivery_board run time: %s  ---" % (datetime.now() - start_time))
        start_time = datetime.now()

        supplier_category = self.supplier_category_distribution.choose_rand(random=Random(10),
                                                                            amount={DeliveryRequest: 100,
                                                                                    DroneLoadingDock: 1})
        fully_connected_graph = create_fully_connected_graph_model(supplier_category, edge_cost_factor=25.0,
                                                                   edge_travel_time_factor=25.0)

        print("--- create_fully_connected_graph_model run time: %s  ---" % (datetime.now() - start_time))
        start_time = datetime.now()

        match_config_file_path = Path('end_to_end/tests/jsons/test_matcher_config.json')
        match_config = MatcherConfig.dict_to_obj(MatcherConfig.json_to_dict(match_config_file_path))
        matcher_input = MatcherInput(graph=fully_connected_graph, empty_board=empty_drone_delivery_board,
                                     config=match_config)

        delivery_board = calc_assignment(matcher_input=matcher_input)
        print("--- calc_assignment run time: %s  ---" % (datetime.now() - start_time))

        print(delivery_board)

        self._draw_matched_scenario(delivery_board, fully_connected_graph, supplier_category, self.mapImage)

    @staticmethod
    def _draw_matched_scenario(delivery_board, fully_connected_graph, supplier_category, map_image):
        dr_drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC, map_image)
        operational_drawer2d.add_operational_graph(dr_drawer, fully_connected_graph, draw_internal=True,
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


if __name__ == '__main__':
    experiment = BasicMinimumEnd2EndExperiment('north')
    experiment.test_small_supplier_category()
