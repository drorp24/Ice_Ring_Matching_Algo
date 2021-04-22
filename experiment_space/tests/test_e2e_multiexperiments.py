import unittest
from datetime import timedelta
from pathlib import Path
from random import Random

from ortools.constraint_solver.routing_enums_pb2 import FirstSolutionStrategy

from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
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
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy, BoardLevelProperties
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeDeltaExtension
from experiment_space.analyzer.quantitative_analyzers import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer, TotalWorkTimeAnalyzer, \
    AmountMatchedPerPackageTypeAnalyzer, MatchingEfficiencyAnalyzer, MatchingPriorityEfficiencyAnalyzer
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

SHOW_VISUALS = True


class EndToEndMultipleExperimentRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('experiment_space/tests/jsons/test_e2e_experiment_config.json')))

    @unittest.skip
    def test_calc_north_scenario_visualization(self):
        sampled_supplier_category = self._create_sampled_supplier_category_north()
        experiment = Experiment(supplier_category=sampled_supplier_category,
                                drone_set_properties_list=EndToEndMultipleExperimentRun.
                                _create_large_drone_set_properties_list(
                                    loading_docks=sampled_supplier_category.drone_loading_docks,
                                    drone_amount=6),
                                matcher_config=self.matcher_config,
                                graph_creation_algorithm=FullyConnectedGraphAlgorithm(edge_cost_factor=25.0,
                                                                                      edge_travel_time_factor=25.0),
                                board_level_properties=BoardLevelProperties())
        map_image = MapImage(map_background_path=Path("visualization/basic/North_map.png"),
                             west_lon=34.907, east_lon=35.905, south_lat=32.489, north_lat=33.932)
        self._run_end_to_end_visual_experiment(experiment, SHOW_VISUALS, map_image)

    @unittest.skip
    def test_calc_center_scenario_visualization(self):
        sampled_supplier_category = self._create_sampled_supplier_category_center()
        experiment = Experiment(supplier_category=sampled_supplier_category,
                                drone_set_properties_list=self._create_even_drone_set_properties_list(
                                    sampled_supplier_category.drone_loading_docks),
                                matcher_config=self.matcher_config,
                                graph_creation_algorithm=FullyConnectedGraphAlgorithm())
        map_image = MapImage(map_background_path=Path("visualization/basic/gush_dan_background.png"),
                             west_lon=34.839, east_lon=35.323, south_lat=31.772, north_lat=32.192)
        self._run_end_to_end_visual_experiment(experiment, SHOW_VISUALS, map_image)

    @unittest.skip
    def test_calc_center_scenario_with_different_first_solution_strategies(self):
        sampled_supplier_category = self._create_sampled_supplier_category_north()
        base_experiment = Experiment(supplier_category=sampled_supplier_category,
                                     drone_set_properties_list=self._create_even_drone_set_properties_list(
                                         sampled_supplier_category.drone_loading_docks),
                                     matcher_config=self.matcher_config,
                                     graph_creation_algorithm=FullyConnectedGraphAlgorithm())
        experiment_options = create_options_class(base_experiment,
                                                  ['Experiment', 'MatcherConfig', 'ORToolsSolverConfig'])

        first_solution_strategies = FirstSolutionStrategy.DESCRIPTOR.enum_values_by_name.keys()

        experiment_options.matcher_config[0].solver[0].first_solution_strategy = first_solution_strategies
        experiments = Options.calc_cartesian_product(experiment_options)

        analyzers = [MatchedDeliveryRequestsAnalyzer,
                     UnmatchedDeliveryRequestsAnalyzer,
                     MatchPercentageDeliveryRequestAnalyzer,
                     TotalWorkTimeAnalyzer,
                     AmountMatchedPerPackageTypeAnalyzer,
                     MatchingEfficiencyAnalyzer]

        results = Experiment.run_multi_match_analysis_pipeline(experiments, analyzers)

        labeled_experiment_analysis = [(str(res[0].matcher_config.solver.first_solution_strategy), res[1])
                                       for res in results]

        draw_labeled_analysis_bar_chart(labeled_experiment_analysis=labeled_experiment_analysis,
                                        analyzer=MatchedDeliveryRequestsAnalyzer,
                                        title='Match percentage per first solution strategy type',
                                        xlabel='First Solution Strategies',
                                        ylabel='Match Percentage of Delivery Requests')

    @unittest.skip
    def test_calc_center_scenario_with_different_fleet_sizes(self):
        sampled_supplier_category = self._create_sampled_supplier_category_north()
        base_experiment = Experiment(supplier_category=sampled_supplier_category,
                                     drone_set_properties_list=self._create_even_drone_set_properties_list(
                                         sampled_supplier_category.drone_loading_docks),
                                     matcher_config=self.matcher_config,
                                     graph_creation_algorithm=FullyConnectedGraphAlgorithm())

        experiment_options = create_options_class(base_experiment, ['Experiment', 'DroneSetProperties'])

        drone_amount_options = list(range(2, 60, 2))
        experiment_options.drone_set_properties[0].drone_amount = drone_amount_options
        experiments = Options.calc_cartesian_product(experiment_options)

        analyzers = [MatchedDeliveryRequestsAnalyzer,
                     UnmatchedDeliveryRequestsAnalyzer,
                     MatchPercentageDeliveryRequestAnalyzer,
                     TotalWorkTimeAnalyzer,
                     AmountMatchedPerPackageTypeAnalyzer,
                     MatchingEfficiencyAnalyzer,
                     MatchingPriorityEfficiencyAnalyzer]

        results = Experiment.run_multi_match_analysis_pipeline(experiments, analyzers)

        labeled_experiment_analysis = [(str(res[0].drone_set_properties_list.drone_amount), res[1])
                                       for res in results]

        draw_labeled_analysis_graph(experiment_analysis=labeled_experiment_analysis,
                                    analyzers=[MatchingEfficiencyAnalyzer, MatchingPriorityEfficiencyAnalyzer],
                                    title='Match Percentage per Fleet Size',
                                    xlabel='Fleet Size',
                                    ylabel='Match Percentage')

    @staticmethod
    def _run_end_to_end_visual_experiment(experiment: Experiment, show_visuals: bool, map_image: MapImage = None):
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
                    drone_station_locations_distribution=UniformPointInBboxDistribution(35.19, 35.19, 32.66, 32.66)),
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
    def _create_even_drone_set_properties_list(cls, loading_docks: [DroneLoadingDock]):
        return [DroneSetProperties(drone_type=DroneType.drone_type_1,
                                   drone_formation_policy=DroneFormationTypePolicy(
                                       {DroneFormationType.PAIR: 0.5, DroneFormationType.QUAD: 0.5}),
                                   package_configuration_policy=PackageConfigurationPolicy(
                                       {PackageConfiguration.LARGE_X2: 1.0}),
                                   start_loading_dock=loading_dock,
                                   end_loading_dock=loading_dock,
                                   drone_amount=30)
                for loading_dock in loading_docks]

    @classmethod
    def _create_uneven_drone_set_properties_list(cls, loading_docks: [DroneLoadingDock]):
        return [DroneSetProperties(drone_type=DroneType.drone_type_1,
                                   drone_formation_policy=DroneFormationTypePolicy(
                                       {DroneFormationType.PAIR: 0.95, DroneFormationType.QUAD: 0.05}),
                                   package_configuration_policy=PackageConfigurationPolicy(
                                       {PackageConfiguration.LARGE_X2: 1.0}),
                                   start_loading_dock=loading_dock,
                                   end_loading_dock=loading_dock,
                                   drone_amount=30)
                for loading_dock in loading_docks]

    @classmethod
    def _create_large_drone_set_properties_list(cls, loading_docks: [DroneLoadingDock], drone_amount: int):
        return [DroneSetProperties(drone_type=DroneType.drone_type_1,
                                   drone_formation_policy=DroneFormationTypePolicy(
                                       {DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0}),
                                   package_configuration_policy=PackageConfigurationPolicy(
                                       {PackageConfiguration.LARGE_X2: 1.0}),
                                   start_loading_dock=loading_dock,
                                   end_loading_dock=loading_dock,
                                   drone_amount=drone_amount)
                for loading_dock in loading_docks]

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
            center_point=create_point_2d(35.46, 33.25),
            sigma_lon=0.2,
            sigma_lat=0.3,
            lowest_priority=10,
            dr_timewindow=20)

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
