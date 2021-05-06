import unittest
from pathlib import Path
from random import Random

from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from experiment_space.analyzer.quantitative_analyzers import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer, TotalWorkTimeAnalyzer, \
    AmountMatchedPerPackageTypeAnalyzer
from experiment_space.experiment import Experiment
from experiment_space.experiment_generator import create_options_class, Options
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm, \
    ClusteredDeliveryRequestGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


class BasicExperimentTest(unittest.TestCase):
    test_json_file_name = Path('experiment_space/tests/jsons/test_writing_experiment.json')

    @classmethod
    def setUpClass(cls):
        supplier_category_path = Path('experiment_space/tests/jsons/test_supplier_category.json')
        cls.supplier_category = SupplierCategory.from_json(supplier_category_path)

        matcher_config_path = Path('experiment_space/tests/jsons/test_matcher_config.json')
        cls.matcher_config = MatcherConfig.from_json(matcher_config_path)

        drone_set_properties_path = Path('experiment_space/tests/jsons/test_drone_set_properties.json')
        drone_set_properties = DroneSetProperties.from_json(drone_set_properties_path)
        cls.drone_set_properties = drone_set_properties

        cls.clustered_graph_creation_algorithm = ClusteredDeliveryRequestGraphAlgorithm(edge_cost_factor=25.0,
                                                                                        edge_travel_time_factor=25.0,
                                                                                        max_clusters_per_zone=3)

        cls.default_graph_creation_algorithm = FullyConnectedGraphAlgorithm()

        cls.experiment = Experiment(supplier_category=cls.supplier_category,
                                    matcher_config=cls.matcher_config,
                                    drone_set_properties_list=[cls.drone_set_properties],
                                    graph_creation_algorithm=cls.default_graph_creation_algorithm)

    @classmethod
    def tearDownClass(cls):
        cls.test_json_file_name.unlink()

    def test_experiment(self):
        result_drone_delivery_board = self.experiment.run_match()

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer]

        analysis_results = Experiment.run_analysis_suite(result_drone_delivery_board, analyzers_to_run)

        self.assertEqual(list(analysis_results.keys()), [a.__name__ for a in analyzers_to_run])
        self.assertEqual(type(analysis_results[MatchedDeliveryRequestsAnalyzer.__name__]), int)
        self.assertEqual(type(analysis_results[UnmatchedDeliveryRequestsAnalyzer.__name__]), int)
        self.assertEqual(type(analysis_results[MatchPercentageDeliveryRequestAnalyzer.__name__]), float)
        self.assertEqual(type(analysis_results[MatchedDeliveryRequestsAnalyzer.__name__]), int)

    def test_cartesian_product_experiments(self):
        experiment_options = create_options_class(self.experiment)
        experiment_options.supplier_category += [self.supplier_category, self.supplier_category]
        experiment_options.matcher_config += [self.matcher_config]

        experiments = Options.calc_cartesian_product(experiment_options)

        result_drone_delivery_boards = [experiment.run_match() for experiment in experiments]

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer]

        analysis_results = [Experiment.run_analysis_suite(result, analyzers_to_run) for result in
                            result_drone_delivery_boards]

        self.assertEqual(len(analysis_results), 6)
        self.assertEqual(len(analysis_results[0].keys()), 5)

    def test_random_k_experiments(self):
        experiment_options = create_options_class(self.experiment)
        experiment_options.supplier_category += [self.supplier_category, self.supplier_category]
        experiment_options.matcher_config += [self.matcher_config]

        experiments = Options.calc_random_k(experiment_options, amount=50, random=Random(100024))

        result_drone_delivery_boards = [experiment.run_match() for experiment in experiments]

        analyzers_to_run = [MatchedDeliveryRequestsAnalyzer,
                            UnmatchedDeliveryRequestsAnalyzer,
                            MatchPercentageDeliveryRequestAnalyzer,
                            TotalWorkTimeAnalyzer,
                            AmountMatchedPerPackageTypeAnalyzer]

        analysis_results = [Experiment.run_analysis_suite(result, analyzers_to_run) for result in
                            result_drone_delivery_boards]

        self.assertEqual(len(analysis_results), 50)
        self.assertEqual(len(analysis_results[0].keys()), 5)

    def test_writing_experiment_json(self):
        self.experiment.to_json(self.test_json_file_name)
        experiments_to_dict = Experiment.json_to_dict(self.test_json_file_name)
        loaded_experiment = Experiment.dict_to_obj(experiments_to_dict)
        self.assertEqual(loaded_experiment, self.experiment)
