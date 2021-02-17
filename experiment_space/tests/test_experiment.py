import unittest
from random import Random

from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from experiment_space.analyzer.quantitative_analyzer import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer, TotalWorkTimeAnalyzer, \
    AmountMatchedPerPackageType
from experiment_space.experiment import Experiment, MultiExperiment
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm, \
    ClusteredDeliveryRequestGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


class BasicExperimentTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        supplier_category_path = 'experiment_space/tests/jsons/test_supplier_category.json'
        cls.supplier_category = SupplierCategory.from_json(SupplierCategory, supplier_category_path)

        matcher_config_path = 'experiment_space/tests/jsons/test_matcher_config.json'
        cls.matcher_config = MatcherConfig.from_json(MatcherConfig, matcher_config_path)

        drone_set_properties_path = 'experiment_space/tests/jsons/test_drone_set_properties.json'
        drone_set_properties = DroneSetProperties.from_json(DroneSetProperties, drone_set_properties_path)
        cls.empty_drone_delivery_board = generate_empty_delivery_board([drone_set_properties])

        cls.clustered_graph_creation_algorithm = ClusteredDeliveryRequestGraphAlgorithm(edge_cost_factor=25.0,
                                                                                        edge_travel_time_factor=25.0,
                                                                                        max_clusters_per_zone=3)

        cls.default_graph_creation_algorithm = FullyConnectedGraphAlgorithm()

    def test_experiment(self):
        experiment = Experiment(supplier_category=self.supplier_category,
                                matcher_config=self.matcher_config,
                                empty_drone_delivery_board=self.empty_drone_delivery_board,
                                graph_creation_algorithm=self.default_graph_creation_algorithm)

        result_drone_delivery_board = experiment.run_experiment()

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer(),
                            UnmatchedDeliveryRequestsAnalyzer(),
                            MatchPercentageDeliveryRequestAnalyzer(),
                            TotalWorkTimeAnalyzer(),
                            AmountMatchedPerPackageType()]

        analysis_results = Experiment.run_analysis_suite(result_drone_delivery_board, analyzers_to_run)

        print(analysis_results)

    def test_cartesian_product_experiments(self):
        experiments = MultiExperiment(
            supplier_categories=[self.supplier_category, self.supplier_category, self.supplier_category],
            matcher_configs=[self.matcher_config, self.matcher_config],
            empty_drone_delivery_boards=[self.empty_drone_delivery_board],
            graph_creation_algorithms=[self.default_graph_creation_algorithm]).calc_cartesian_product_experiments()

        result_drone_delivery_boards = [experiment.run_experiment() for experiment in experiments]

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer(),
                            UnmatchedDeliveryRequestsAnalyzer(),
                            MatchPercentageDeliveryRequestAnalyzer(),
                            TotalWorkTimeAnalyzer(),
                            AmountMatchedPerPackageType()]

        analysis_results = [Experiment.run_analysis_suite(result, analyzers_to_run) for result in
                            result_drone_delivery_boards]

        self.assertEqual(len(analysis_results), 6)
        self.assertEqual(len(analysis_results[0].keys()), 5)

    def test_random_k_experiments(self):
        experiments = MultiExperiment(
            supplier_categories=[self.supplier_category, self.supplier_category, self.supplier_category],
            matcher_configs=[self.matcher_config, self.matcher_config],
            empty_drone_delivery_boards=[self.empty_drone_delivery_board],
            graph_creation_algorithms=[self.default_graph_creation_algorithm]) \
            .calc_random_k_experiments(random=Random(42), amount=50)

        result_drone_delivery_boards = [experiment.run_experiment() for experiment in experiments]

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer(),
                            UnmatchedDeliveryRequestsAnalyzer(),
                            MatchPercentageDeliveryRequestAnalyzer(),
                            TotalWorkTimeAnalyzer(),
                            AmountMatchedPerPackageType()]

        analysis_results = [Experiment.run_analysis_suite(result, analyzers_to_run) for result in
                            result_drone_delivery_boards]

        self.assertEqual(len(analysis_results), 50)
        self.assertEqual(len(analysis_results[0].keys()), 5)
