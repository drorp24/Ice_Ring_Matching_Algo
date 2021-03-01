import unittest
from pathlib import Path

from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy
from common.entities.base_entities.package import PackageType
from experiment_space.analyzer.quantitative_analyzer import AmountMatchedPerPackageType, \
    UnmatchedDeliveryRequestsAnalyzer
from experiment_space.experiment import Experiment
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


class BasicMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategory.dict_to_obj(SupplierCategory.json_to_dict(
            Path('end_to_end/tests/jsons/test_supplier_category.json')))
        cls.empty_drone_delivery_board = \
            generate_empty_delivery_board([BasicMinimumEnd2End._create_simple_drone_set_properties()])
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('end_to_end/tests/jsons/test_matcher_config.json')))

    @classmethod
    def _create_simple_drone_set_properties(cls):
        return DroneSetProperties(drone_type=DroneType.drone_type_1,
                                  drone_formation_policy=DroneFormationTypePolicy(
                                      {DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0}),
                                  package_configuration_policy=PackageConfigurationPolicy(
                                      {PackageConfiguration.LARGE_X2: 0.6, PackageConfiguration.MEDIUM_X4: 0.2,
                                       PackageConfiguration.SMALL_X8: 0.2, PackageConfiguration.TINY_X16: 0.0}),
                                  drone_amount=30)

    def test_create_graph_model(self):
        operational_graph = FullyConnectedGraphAlgorithm().create(self.supplier_category)
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    def test_calc_assignment(self):
        e = Experiment(supplier_category=self.supplier_category,
                       empty_drone_delivery_board=self.empty_drone_delivery_board,
                       matcher_config=self.matcher_config,
                       graph_creation_algorithm=FullyConnectedGraphAlgorithm())

        delivery_board = e.run_match()

        analysis = Experiment.run_analysis_suite(delivery_board,
                                                 [UnmatchedDeliveryRequestsAnalyzer,
                                                  AmountMatchedPerPackageType])

        unmatched_delivery_requests = analysis[AmountMatchedPerPackageType.__name__]
        self.assertEqual(len(unmatched_delivery_requests), 4)

        amount_per_package_type = analysis[AmountMatchedPerPackageType.__name__]
        self.assertEqual(amount_per_package_type.get(PackageType.TINY), 1)
        self.assertEqual(amount_per_package_type.get(PackageType.MEDIUM), 1)
        self.assertEqual(amount_per_package_type.get(PackageType.LARGE), 4)
