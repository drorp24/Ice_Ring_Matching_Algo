import unittest
from pathlib import Path

from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy, BoardLevelProperties
from common.entities.base_entities.package import PackageType
from experiment_space.analyzer.quantitative_analyzers import AmountMatchedPerPackageTypeAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer
from experiment_space.experiment import Experiment
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


class BasicMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategory.dict_to_obj(SupplierCategory.json_to_dict(
            Path('experiment_space/tests/jsons/test_supplier_category.json')))
        cls.drone_set_properties = BasicMinimumEnd2End._create_simple_drone_set_properties()
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('experiment_space/tests/jsons/test_min_e2e_config.json')))

    @classmethod
    def _create_simple_drone_set_properties(cls):
        return DroneSetProperties(drone_type=DroneType.drone_type_1,
                                  drone_formation_policy=DroneFormationTypePolicy(
                                      {DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0}),
                                  package_configuration_policy=PackageConfigurationPolicy(
                                      {PackageConfiguration.LARGE_X2: 0.4, PackageConfiguration.MEDIUM_X4: 0.2,
                                       PackageConfiguration.SMALL_X8: 0.2, PackageConfiguration.TINY_X16: 0.2}),
                                  drone_amount=50)

    def test_create_graph_model(self):
        operational_graph = FullyConnectedGraphAlgorithm().create(self.supplier_category)
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    def test_calc_assignment(self):
        e = Experiment(supplier_category=self.supplier_category,
                       drone_set_properties=self.drone_set_properties,
                       matcher_config=self.matcher_config,
                       graph_creation_algorithm=FullyConnectedGraphAlgorithm(),
                       board_level_properties=BoardLevelProperties(400, 10.0))

        delivery_board = e.run_match()

        analysis = Experiment.run_analysis_suite(delivery_board,
                                                 [UnmatchedDeliveryRequestsAnalyzer,
                                                  AmountMatchedPerPackageTypeAnalyzer])

        unmatched_delivery_requests = analysis[AmountMatchedPerPackageTypeAnalyzer.__name__]
        self.assertEqual(len(unmatched_delivery_requests), 4)

        amount_per_package_type = analysis[AmountMatchedPerPackageTypeAnalyzer.__name__]
        self.assertEqual(amount_per_package_type.get(PackageType.TINY), 1)
        self.assertEqual(amount_per_package_type.get(PackageType.MEDIUM), 1)
        self.assertEqual(amount_per_package_type.get(PackageType.LARGE), 4)
