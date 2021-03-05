import unittest
from datetime import timedelta, date, time
from pathlib import Path
from random import Random

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
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import build_empty_drone_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeDeltaExtension, DateTimeExtension
from experiment_space.analyzer.quantitative_analyzer import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer, TotalWorkTimeAnalyzer, \
    AmountMatchedPerPackageTypeAnalyzer, MatchingEfficiencyAnalyzer
from experiment_space.distribution.supplier_category_distribution import SupplierCategoryDistribution
from experiment_space.experiment import Experiment
from experiment_space.experiment_generator import create_options_class, Options
from experiment_space.tests.test_clustered_graph_experiments import _create_standard_full_day_test_time, ZERO_TIME, \
    FullyConnectedGraphAlgorithm, DeliveryRequest
from experiment_space.visualization.experiment_visualizer import draw_matched_scenario, \
    draw_labeled_analysis_bar_chart, draw_labeled_analysis_graph
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
SHOW_VISUALS = True


class EndToEndMultipleExperimentRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.drone_set_properties = EndToEndMultipleExperimentRun._create_regular_drone_set_properties()
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('experiment_space/tests/jsons/test_matcher_config.json')))

    @unittest.skip
    def test_calc_north_scenario_visualization(self):
        sampled_supplier_category = self._create_sampled_supplier_category_north()
        experiment = Experiment(supplier_category=sampled_supplier_category,
                                drone_set_properties=EndToEndMultipleExperimentRun._create_large_drone_set_properties(),
                                matcher_config=self.matcher_config,
                                graph_creation_algorithm=FullyConnectedGraphAlgorithm())
        EndToEndMultipleExperimentRun._run_end_to_end_visual_experiment(experiment, SHOW_VISUALS)

    @unittest.skip
    def test_calc_center_scenario_visualization(self):
        sampled_supplier_category = self._create_sampled_supplier_category_center()
        experiment = Experiment(supplier_category=sampled_supplier_category,
                                drone_set_properties=self.drone_set_properties,
                                matcher_config=self.matcher_config,
                                graph_creation_algorithm=FullyConnectedGraphAlgorithm())
        EndToEndMultipleExperimentRun._run_end_to_end_visual_experiment(experiment, SHOW_VISUALS)

    @unittest.skip
    def test_calc_center_scenario_with_different_first_solution_strategies(self):
        sampled_supplier_category = self._create_sampled_supplier_category_center()
        experiment = Experiment(supplier_category=sampled_supplier_category,
                                drone_set_properties=self.drone_set_properties,
                                matcher_config=self.matcher_config,
                                graph_creation_algorithm=FullyConnectedGraphAlgorithm())
        experiment_options = create_options_class(experiment, ['Experiment', 'MatcherConfig', 'ORToolsSolverConfig'])

        first_solution_strategies = ['UNSET', 'AUTOMATIC', 'PATH_CHEAPEST_ARC', 'PATH_MOST_CONSTRAINED_ARC',
                                     'EVALUATOR_STRATEGY', 'SAVINGS', 'SWEEP', 'CHRISTOFIDES', 'ALL_UNPERFORMED',
                                     'BEST_INSERTION', 'PARALLEL_CHEAPEST_INSERTION', 'SEQUENTIAL_CHEAPEST_INSERTION',
                                     'LOCAL_CHEAPEST_INSERTION', 'GLOBAL_CHEAPEST_ARC', 'LOCAL_CHEAPEST_ARC',
                                     'FIRST_UNBOUND_MIN_VALUE']
        experiment_options.matcher_config[0].solver[0].first_solution_strategy = first_solution_strategies
        experiments = Options.calc_cartesian_product(experiment_options)

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer,
                            MatchingEfficiencyAnalyzer]

        labeled_results = [(str(labeled_experiment[0]),
                            Experiment.run_analysis_suite(labeled_experiment[1].run_match(), analyzers_to_run))
                           for labeled_experiment in zip(first_solution_strategies, experiments)]

        draw_labeled_analysis_bar_chart(labeled_experiment_analysis=labeled_results,
                                        analyzer=MatchPercentageDeliveryRequestAnalyzer,
                                        title='Match percentage per first solution strategy type',
                                        xlabel='First Solution Strategies',
                                        ylabel='Match Percentage of Delivery Requests')

    # @unittest.skip
    def test_calc_center_scenario_with_different_fleet_sizes(self):
        sampled_supplier_category = self._create_sampled_supplier_category_north()
        experiment = Experiment(supplier_category=sampled_supplier_category,
                                drone_set_properties=self.drone_set_properties,
                                matcher_config=self.matcher_config,
                                graph_creation_algorithm=FullyConnectedGraphAlgorithm())

        experiment_options = create_options_class(experiment, ['Experiment', 'DroneSetProperties'])

        drone_amount_options = list(range(2, 51, 3))
        experiment_options.drone_set_properties[0].drone_amount = drone_amount_options
        experiments = Options.calc_cartesian_product(experiment_options)

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer,
                            MatchingEfficiencyAnalyzer]

        labeled_results = [(str(labeled_experiment[0]),
                            Experiment.run_analysis_suite(labeled_experiment[1].run_match(), analyzers_to_run))
                           for labeled_experiment in zip(drone_amount_options, experiments)]

        draw_labeled_analysis_graph(labeled_experiment_analysis=labeled_results,
                                    analyzer=MatchPercentageDeliveryRequestAnalyzer,
                                    title='Match percentage per fleet size',
                                    xlabel='Fleet Size',
                                    ylabel='Match Percentage of Delivery Requests')

        draw_labeled_analysis_graph(labeled_experiment_analysis=labeled_results,
                                    analyzer=MatchingEfficiencyAnalyzer,
                                    title='Match percentage per fleet size',
                                    xlabel='Fleet Size',
                                    ylabel='Match Efficiency')

    @staticmethod
    def _run_end_to_end_visual_experiment(experiment: Experiment, show_visuals: bool):
        graph = experiment.graph_creation_algorithm.create(experiment.supplier_category)
        result_drone_delivery_board = experiment.run_match()
        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer,
                            MatchingEfficiencyAnalyzer]
        analysis_results = Experiment.run_analysis_suite(result_drone_delivery_board, analyzers_to_run)
        print(analysis_results)
        if show_visuals:
            map_image = MapImage(map_background_path=Path("visualization/basic/gush_dan_background.png"),
                                 west_lon=west_lon, east_lon=east_lon, south_lat=south_lat, north_lat=north_lat)
            draw_matched_scenario(delivery_board=result_drone_delivery_board, graph=graph,
                                  supplier_category=experiment.supplier_category, map_image=map_image)
        return analysis_results

    @classmethod
    def _create_sampled_supplier_category_north(cls):
        return SupplierCategoryDistribution(
            zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
            delivery_requests_distribution=cls._create_custom_delivery_request_distribution_north(),
            drone_loading_docks_distribution=DroneLoadingDockDistribution(
                drone_loading_station_distributions=DroneLoadingStationDistribution(
                    drone_station_locations_distribution=UniformPointInBboxDistribution(35.11, 35.11, 31.79, 31.79)),
                time_window_distributions=_create_standard_full_day_test_time())).choose_rand(Random(42), amount={
            DeliveryRequest: 50})[0]

    @classmethod
    def _create_sampled_supplier_category_center(cls):
        return SupplierCategoryDistribution(
            zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
            delivery_requests_distribution=cls._create_custom_delivery_request_distribution_center(),
            drone_loading_docks_distribution=DroneLoadingDockDistribution(
                drone_loading_station_distributions=DroneLoadingStationDistribution(
                    drone_station_locations_distribution=UniformPointInBboxDistribution(35.11, 35.11, 31.79, 31.79)),
                time_window_distributions=_create_standard_full_day_test_time())).choose_rand(Random(42), amount={
            DeliveryRequest: 25})[0]

    @classmethod
    def _create_regular_drone_set_properties(cls):
        return DroneSetProperties(drone_type=DroneType.drone_type_1,
                                  drone_formation_policy=DroneFormationTypePolicy(
                                      {DroneFormationType.PAIR: 0.9, DroneFormationType.QUAD: 0.1}),
                                  package_configuration_policy=PackageConfigurationPolicy(
                                      {PackageConfiguration.LARGE_X2: 1.0}),
                                  drone_amount=30)

    @classmethod
    def _create_large_drone_set_properties(cls):
        return DroneSetProperties(drone_type=DroneType.drone_type_1,
                                  drone_formation_policy=DroneFormationTypePolicy(
                                      {DroneFormationType.PAIR: 0.9, DroneFormationType.QUAD: 0.1}),
                                  package_configuration_policy=PackageConfigurationPolicy(
                                      {PackageConfiguration.LARGE_X2: 1.0}),
                                  drone_amount=100)

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
    def _create_custom_delivery_request_distribution_north():
        return EndToEndMultipleExperimentRun._create_delivery_request_distribution(
            center_point=create_point_2d(35.11, 32.0),
            sigma_lat=0.12,
            sigma_lon=0.08,
            lowest_priority=10,
            dr_timewindow=3)

    @staticmethod
    def _create_custom_delivery_request_distribution_center():
        return EndToEndMultipleExperimentRun._create_delivery_request_distribution(
            center_point=create_point_2d(35.11, 31.84),
            sigma_lat=0.04,
            sigma_lon=0.06,
            lowest_priority=10,
            dr_timewindow=2)

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
