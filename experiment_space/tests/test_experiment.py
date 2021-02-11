import unittest

from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from experiment_space.analyzer.quantitative_analyzer import MatchedDeliveryRequestsAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer, MatchPercentageDeliveryRequestAnalyzer
from experiment_space.experiment import Experiment
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

    def test_experiment(self):
        experiment = Experiment(supplier_category=self.supplier_category,
                                matcher_config=self.matcher_config,
                                empty_drone_delivery_board=self.empty_drone_delivery_board)

        result_drone_delivery_board = experiment.run_experiment()

        analysis_results = Experiment.run_analysis_suite(result_drone_delivery_board,
                                                         [MatchedDeliveryRequestsAnalyzer(),
                                                          UnmatchedDeliveryRequestsAnalyzer(),
                                                          MatchPercentageDeliveryRequestAnalyzer()])

        print(analysis_results)
