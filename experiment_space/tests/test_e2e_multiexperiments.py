import unittest
from datetime import timedelta, date, time
from pathlib import Path

from common.entities.base_entities.drone import DroneType, PackageConfiguration
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
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board, \
    build_empty_drone_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeDeltaExtension, DateTimeExtension
from experiment_space.analyzer.quantitative_analyzer import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer, TotalWorkTimeAnalyzer, \
    AmountMatchedPerPackageTypeAnalyzer, MatchingEfficiencyAnalyzer
from experiment_space.experiment import Experiment
from experiment_space.supplier_category import SupplierCategory
from experiment_space.tests.test_clustered_graph_experiments import _create_standard_full_day_test_time, ZERO_TIME, \
    FullyConnectedGraphAlgorithm
from experiment_space.visualization.experiment_visualizer import draw_matched_scenario
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, NormalPointDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d
from matching.matcher_config import MatcherConfig
from visualization.basic.pltdrawer2d import MapImage

west_lon = 34.83927
east_lon = 35.32341
south_lat = 31.77279
north_lat = 32.19276

ZERO_TIME = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(0, 0, 0))


class EndToEndMultipleExperimentRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategory.dict_to_obj(
            SupplierCategory.json_to_dict(Path('end_to_end/tests/jsons/test_supplier_category.json')))
        cls.empty_drone_delivery_board = generate_empty_delivery_board(
            [EndToEndMultipleExperimentRun._create_simple_drone_set_properties()])
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('end_to_end/tests/jsons/test_matcher_config.json')))

    def test_calc_center_scenario(self):
        print('!!' + self.__str__())

    def test_calc_center_scenario2(self):
        print('!!' + self.__str__())

    def test_calc_center_scenario3(self):
        drone_station_location = create_point_2d(35.11, 31.79)

        sampled_supplier_category = self.supplier_category

        experiment = Experiment(supplier_category=sampled_supplier_category,
                                empty_drone_delivery_board=self.empty_drone_delivery_board,
                                matcher_config=self.matcher_config,
                                graph_creation_algorithm=FullyConnectedGraphAlgorithm())

        graph = FullyConnectedGraphAlgorithm().create(sampled_supplier_category)

        result_drone_delivery_board = experiment.run_match()

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer,
                            MatchingEfficiencyAnalyzer]

        analysis_results = Experiment.run_analysis_suite(result_drone_delivery_board, analyzers_to_run)

        print(analysis_results)

        map_image = MapImage(map_background_path=Path(r"visualization/basic/gush_dan_background.Png"),
                             west_lon=west_lon, east_lon=east_lon, south_lat=south_lat, north_lat=north_lat)

        draw_matched_scenario(delivery_board=result_drone_delivery_board, graph=graph,
                              supplier_category=sampled_supplier_category, map_image=map_image)

        self.assertEqual(1, 1)

    @classmethod
    def _create_simple_drone_set_properties(cls):
        return DroneSetProperties(drone_type=DroneType.drone_type_1,
                                  drone_formation_policy=DroneFormationTypePolicy(
                                      {DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0}),
                                  package_configuration_policy=PackageConfigurationPolicy(
                                      {PackageConfiguration.LARGE_X2: 0.8, PackageConfiguration.MEDIUM_X4: 0.1,
                                       PackageConfiguration.SMALL_X8: 0.1, PackageConfiguration.TINY_X16: 0.0}),
                                  drone_amount=30)

    @staticmethod
    def _create_custom_drone_loading_dock_distribution(drone_station_location):
        return DroneLoadingDockDistribution(
            drone_loading_station_distributions=DroneLoadingStationDistribution(
                drone_station_locations_distribution=UniformPointInBboxDistribution(drone_station_location.x,
                                                                                    drone_station_location.x,
                                                                                    drone_station_location.y,
                                                                                    drone_station_location.y)),
            time_window_distributions=_create_standard_full_day_test_time())

    @staticmethod
    def _create_custom_delivery_request_distribution():
        return EndToEndMultipleExperimentRun._create_delivery_request_distribution(
            center_point=create_point_2d(35.11, 32.0),
            sigma_lat=0.03,
            sigma_lon=0.05,
            lowest_priority=10,
            dr_timewindow=3)

    @staticmethod
    def _create_standard_full_day_test_time():
        default_start = ZERO_TIME
        default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=23, minutes=59))])
        default_dt_options = [default_start]
        return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)

    @staticmethod
    def _create_large_package_only_distribution():
        package_type_distribution_dict = {PackageType.LARGE: 1}
        package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
        return package_distribution

    @staticmethod
    def _create_delivery_request_distribution(center_point: Point2D, sigma_lon: float, sigma_lat: float,
                                              lowest_priority: int = 10, dr_timewindow: int = 3):
        package_distribution = EndToEndMultipleExperimentRun._create_large_package_only_distribution()
        zero_time = ZERO_TIME
        time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=dr_timewindow, minutes=0))])
        dt_options = [zero_time.add_time_delta(TimeDeltaExtension(timedelta(hours=x))) for x in
                      range(24 - dr_timewindow)]

        time_window_distribution = TimeWindowDistribution(DateTimeDistribution(dt_options), time_delta_distrib)

        delivery_request_distribution = build_delivery_request_distribution(
            package_type_distribution=package_distribution,
            relative_dr_location_distribution=NormalPointDistribution(center_point, sigma_lon, sigma_lat),
            priority_distribution=PriorityDistribution(list(range(1, lowest_priority))),
            time_window_distribution=time_window_distribution)
        return delivery_request_distribution

    @staticmethod
    def _create_basic_package_configuration():
        return PackageConfigurationPolicy({PackageConfiguration.LARGE_X2: 0.9,
                                           PackageConfiguration.MEDIUM_X4: 0.1,
                                           PackageConfiguration.SMALL_X8: 0,
                                           PackageConfiguration.TINY_X16: 0})

    @staticmethod
    def _create_basic_empty_drone_delivery_board(
            drone_formation_policy=DroneFormationTypePolicy({DroneFormationType.PAIR: 1, DroneFormationType.QUAD: 0}),
            package_configurations_policy=None,
            drone_type: DroneType = DroneType.drone_type_1,
            amount: int = 30, max_route_time_entire_board: int = 400, velocity_entire_board: float = 10.0):
        drone_set_properties = DroneSetProperties(drone_type=drone_type,
                                                  package_configuration_policy=package_configurations_policy,
                                                  drone_formation_policy=drone_formation_policy,
                                                  drone_amount=amount)
        return build_empty_drone_delivery_board(drone_set_properties, max_route_time_entire_board,
                                                velocity_entire_board)
