from datetime import time, date, timedelta, datetime
from pathlib import Path
from random import Random, sample

import numpy as np
from networkx.drawing.tests.test_pylab import plt

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
from experiment_space.distribution.supplier_category_distribution import SupplierCategoryDistribution
from experiment_space.graph_creation_algorithm import *
from geometry.distribution.geo_distribution import NormalPointDistribution, UniformPointInBboxDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d
from matching.matcher_config import MatcherConfig
from visualization.basic.pltdrawer2d import MapImage

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

    def __init__(self, scene: str, lowest_priority: int = 10, dr_timewindow: int = 3):
        self.matcher_config = Path("end_to_end/tests/jsons/test_matcher_config.json")
        self.lowest_priority = lowest_priority
        self.dr_timewindow = dr_timewindow
        if scene == 'north':
            self.supplier_category_distribution = SupplierCategoryDistribution(
                zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
                delivery_requests_distribution=_create_delivery_request_distribution(
                    create_point_2d(35.45, 33.4 - 0.5 * 1), 0.05, 0.06, lowest_priority, dr_timewindow),
                drone_loading_docks_distribution=DroneLoadingDockDistribution(
                    drone_loading_station_distributions=DroneLoadingStationDistribution(
                        drone_station_locations_distribution=UniformPointInBboxDistribution(35.19336,
                                                                                            35.19336,
                                                                                            32.6675,
                                                                                            32.6675
                                                                                            )),
                    time_window_distributions=create_standard_full_day_test_time()))
            self.mapImage = MapImage(map_background_path=Path(r"visualization/basic/north_map.Png"),
                                     west_lon=34.90777, east_lon=35.90753, south_lat=32.48928, north_lat=33.93233)
        elif scene == 'center':
            self.supplier_category_distribution = SupplierCategoryDistribution(
                zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
                delivery_requests_distribution=_create_delivery_request_distribution(create_point_2d(35.11, 32.0), 0.03,
                                                                                     0.05, lowest_priority,
                                                                                     dr_timewindow),
                drone_loading_docks_distribution=DroneLoadingDockDistribution(
                    drone_loading_station_distributions=DroneLoadingStationDistribution(
                        drone_station_locations_distribution=UniformPointInBboxDistribution(35.11,
                                                                                            35.11,
                                                                                            31.79, 31.79
                                                                                            )),
                    time_window_distributions=create_standard_full_day_test_time()))
            self.matcher_config = Path("end_to_end/tests/jsons/test_matcher_config.json")
            self.mapImage = MapImage(map_background_path=Path(r"visualization/basic/gush_dan_background.Png"),
                                     west_lon=34.83927, east_lon=35.32341, south_lat=31.77279, north_lat=32.19276)

    def test_small_supplier_category(self, drones_amount=20, drone_max_route_time=45,
                                     delivery_request_amount=37, seed=10, print_flag=True, draw_flag=True):
        start_time = datetime.now()
        empty_drone_delivery_board = _create_empty_drone_delivery_board(amount=drones_amount,
                                                                        max_route_time_entire_board=drone_max_route_time,
                                                                        velocity_entire_board=10.0)
        if print_flag:
            print("--- _create_empty_drone_delivery_board run time: %s  ---" % (datetime.now() - start_time))
        start_time = datetime.now()

        supplier_category = self.supplier_category_distribution.choose_rand(random=Random(seed),
                                                                            amount={
                                                                                DeliveryRequest: delivery_request_amount,
                                                                                DroneLoadingDock: 1})
        fully_connected_graph = create_fully_connected_graph_model(supplier_category, edge_travel_time_factor=70.0)
        if print_flag:
            print("--- create_fully_connected_graph_model run time: %s  ---" % (datetime.now() - start_time))
        start_time = datetime.now()

        match_config_file_path = Path('end_to_end/tests/jsons/test_matcher_config.json')
        match_config = MatcherConfig.dict_to_obj(MatcherConfig.json_to_dict(match_config_file_path))
        matcher_input = MatcherInput(graph=fully_connected_graph, empty_board=empty_drone_delivery_board,
                                     config=match_config)

        delivery_board = calc_assignment(matcher_input=matcher_input)
        assignment_run_time = datetime.now() - start_time
        if print_flag:
            print("--- calc_assignment run time: %s  ---" % assignment_run_time)
            print(delivery_board)

        num_unmatched_dr = len(delivery_board.unmatched_delivery_requests)
        total_priority = fully_connected_graph.calc_total_priority()
        unmatched_priority = total_priority - delivery_board.get_total_priority()
        priority_eff = 100.0 * (1 - (self.lowest_priority * num_unmatched_dr - unmatched_priority) /
                                (self.lowest_priority * delivery_request_amount - total_priority))
        matching_eff = 100.0 * (1.0 - num_unmatched_dr / delivery_request_amount)

        if draw_flag:
            self._draw_matched_scenario(delivery_board, fully_connected_graph, supplier_category, self.mapImage)

        return [priority_eff, matching_eff, assignment_run_time.total_seconds()]

    def e2e_analysis(self, drones_amount_list, delivery_request_amount_list, seed_list=[10]):
        performance_matrix = np.zeros((len(drones_amount_list), len(delivery_request_amount_list), len(seed_list), 3))
        for i, drones_amount in enumerate(drones_amount_list):
            for j, delivery_request_amount in enumerate(delivery_request_amount_list):
                for k, seed in enumerate(seed_list):
                    performance_matrix[i, j, k, :] = self.test_small_supplier_category(drones_amount=drones_amount,
                                                                                       delivery_request_amount=
                                                                                       delivery_request_amount,
                                                                                       seed=seed,
                                                                                       print_flag=False,
                                                                                       draw_flag=False)
        return performance_matrix


if __name__ == '__main__':

    scene = 'center'  # 'center', 'north'
    mode = 'single'  # 'single', 'sweep_drones', 'sweep_requests', 'sweep_seed' ;

    experiment = BasicMinimumEnd2EndExperiment(scene)

    if mode == 'single':
        [priority_eff, matching_eff, assignment_run_time] = experiment.test_small_supplier_category(drones_amount=20,
                                                                                                    drone_max_route_time=50,
                                                                                                    delivery_request_amount=37)
    if mode == 'sweep_drones':
        drones_amount_list = list(range(4, 32, 2))
        delivery_request_amount_list = [37, 60]
        seed_list = [10]
        analysis_matrix = experiment.e2e_analysis(drones_amount_list, delivery_request_amount_list, seed_list)

        for idx, amount in enumerate(delivery_request_amount_list):
            fig = plt.figure(idx)
            ax = plt.subplot(111)
            ax.plot(drones_amount_list, np.squeeze(analysis_matrix[:, idx, 0, 1]),
                    'ro-', linewidth=2, markersize=10, markerfacecolor='blue', label="Package delivered")
            ax.plot(drones_amount_list, np.squeeze(analysis_matrix[:, idx, 0, 0]),
                    'gs--', linewidth=2, markersize=7, markerfacecolor='darkorange', label="Priority weighted")
            ax.set_xlabel('Number of vehicles')
            ax.set_ylabel('Delivering Efficiency [%]')
            ax.set_title('Delivering Efficiency vs. Fleet Size (%s requests)' % amount)
            ax.set_xlim(0, drones_amount_list[-1] + 1)
            ax.set_ylim(0, 105)
            ax.grid('on')
            plt.legend(loc='upper left')

    if mode == 'sweep_requests':
        drones_amount_list = [20]
        delivery_request_amount_list = list(range(10, 120, 10))
        seed_list = [10]
        analysis_matrix = experiment.e2e_analysis(drones_amount_list, delivery_request_amount_list, seed_list)

        for idx, amount in enumerate(drones_amount_list):
            fig = plt.figure(idx)
            ax = plt.subplot(111)
            ax.plot(delivery_request_amount_list, np.squeeze(analysis_matrix[idx, :, 0, 1]),
                    'ro-', linewidth=2, markersize=10, markerfacecolor='blue', label="Package delivered")
            ax.plot(delivery_request_amount_list, np.squeeze(analysis_matrix[idx, :, 0, 0]),
                    'gs--', linewidth=2, markersize=7, markerfacecolor='darkorange', label="Priority weighted")
            ax.set_xlabel('Number of delivery requests')
            ax.set_ylabel('Delivering Efficiency [%]')
            ax.set_title('Delivering Efficiency vs. Demand Size (%s drones)' % amount)
            ax.set_xlim(0, delivery_request_amount_list[-1] + 1)
            ax.set_ylim(0, 105)
            ax.grid('on')
            plt.legend(loc='lower left')

    if mode == 'sweep_seed':
        drones_amount_list = [20]
        delivery_request_amount_list = [60]
        seed_list = sample(range(10, 1000), 25)
        analysis_matrix = experiment.e2e_analysis(drones_amount_list, delivery_request_amount_list, seed_list)
        for idx, amount in enumerate(drones_amount_list):
            fig = plt.figure(idx)
            ax = plt.subplot(111)
            ax.plot()
            plt.hist([np.squeeze(analysis_matrix[idx, 0, :, 1]), np.squeeze(analysis_matrix[idx, 0, :, 0])],
                     color=['b', 'g'], alpha=0.5, label=["Package delivered", "Priority weighted"])
            ax.set_xlabel('Delivering Efficiency [%]')
            ax.set_title('Delivering Efficiency Histogram variable Seed (%s drones, %s requests)' % (
            amount, delivery_request_amount_list[0]))
            plt.legend(loc='upper right')

    plt.show()
