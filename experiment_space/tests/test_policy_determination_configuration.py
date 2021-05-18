import unittest
from pathlib import Path
from common.entities.base_entities.fleet.policy_determination import FleetPolicyDeterminationAttribution
from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy, BoardLevelProperties
from common.entities.base_entities.package import PackageType
from experiment_space.analyzer.quantitative_analyzers import AmountMatchedPerPackageTypeAnalyzer, \
    UnmatchedDeliveryRequestsAnalyzer
from experiment_space.experiment import Experiment
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


class BasicMinimumEnd2EndWithPolicyCalculation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategory.dict_to_obj(SupplierCategory.json_to_dict(
            Path('experiment_space/tests/jsons/test_supplier_category.json')))

        cls.req_dict = dict ()
        for typePackage in PackageType:
            cls.req_dict [typePackage] = 0

        for i in range (len(cls.supplier_category.delivery_requests)):
            typePackage = cls.supplier_category.delivery_requests[i].delivery_options[0].customer_deliveries[0].package_delivery_plans[0].package_type
            cls.req_dict [typePackage] = cls.req_dict [typePackage] + 1

        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('experiment_space/tests/jsons/test_min_e2e_config.json')))

        cls.drone_set_properties_list = BasicMinimumEnd2EndWithPolicyCalculation._create_simple_drone_set_properties_list(
            cls.supplier_category.drone_loading_docks)


    @classmethod
    def _create_simple_drone_set_properties_list(cls, loading_docks: [DroneLoadingDock]):
        return [DroneSetProperties(drone_type=DroneType.drone_type_1,
                                   drone_formation_policy=DroneFormationTypePolicy(
                                       {DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0}),
                                   package_configuration_policy=PackageConfigurationPolicy(
                                       {PackageConfiguration.LARGE_X2: 0.4, PackageConfiguration.MEDIUM_X4: 0.2,
                                        PackageConfiguration.SMALL_X8: 0.2, PackageConfiguration.TINY_X16: 0.2}),
                                   start_loading_dock=loading_dock,
                                   end_loading_dock=loading_dock,
                                   drone_amount=5)
                for loading_dock in loading_docks]

    def test_creation_of_policies (self):
        FleetPolicyDeterminationAttribution.extract_parameters(self.drone_set_properties_list, self.matcher_config,
                                                               self.req_dict)
        policies = FleetPolicyDeterminationAttribution.solve()
        print (policies)
        for drone_set_properties in self.drone_set_properties_list:
            drone_set_properties.package_configuration_policy = policies.policies[drone_set_properties.start_loading_dock]
            print (policies.policies[drone_set_properties.start_loading_dock])


    def test_create_graph_model(self):
        operational_graph = FullyConnectedGraphAlgorithm().create(self.supplier_category)
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    def test_calc_assignment(self):
        e = Experiment(supplier_category=self.supplier_category,
                       drone_set_properties_list=self.drone_set_properties_list,
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
        self.assertEqual(amount_per_package_type.get(PackageType.TINY), 0)
        self.assertEqual(amount_per_package_type.get(PackageType.MEDIUM), 0)
        self.assertEqual(amount_per_package_type.get(PackageType.LARGE), 2)
        self.assertEqual(amount_per_package_type.get(PackageType.SMALL), 0)
