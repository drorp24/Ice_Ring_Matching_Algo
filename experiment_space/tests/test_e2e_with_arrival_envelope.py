import os
import unittest
from pathlib import Path

from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy, BoardLevelProperties
from common.entities.base_entities.package import PackageType
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


class BasicArrivalEnvelopeMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategory.dict_to_obj(SupplierCategory.json_to_dict(
            Path('experiment_space/tests/jsons/test_supplier_category.json')))
        cls.empty_drone_delivery_board = \
            generate_empty_delivery_board(
                drone_set_properties=[BasicArrivalEnvelopeMinimumEnd2End._create_simple_drone_set_properties()],
                board_level_properties=BoardLevelProperties(max_route_time_entire_board=400,
                                                            velocity_entire_board=10))
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
                                  drone_amount=30)

    def test_create_graph_model(self):
        operational_graph = FullyConnectedGraphAlgorithm(edge_cost_factor=1, edge_travel_time_factor=1) \
            .create(supplier_category=self.supplier_category)
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    @unittest.skipIf(os.environ.get('NO_SLOW_TESTS', False), 'slow tests')
    def test_calc_assignment(self):
        operational_graph = FullyConnectedGraphAlgorithm(edge_cost_factor=1, edge_travel_time_factor=1) \
            .create(supplier_category=self.supplier_category)

        matcher_input = MatcherInput(graph=operational_graph,
                                     empty_board=self.empty_drone_delivery_board,
                                     config=self.matcher_config)

        delivery_board = create_matcher(matcher_input).match()
        self.assertEqual(len(delivery_board.unmatched_delivery_requests), 4)
        amount_per_package_type = delivery_board.get_total_amount_per_package_type()
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.TINY), 1)
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.MEDIUM), 1)
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.LARGE), 4)
        self.assertEqual(delivery_board.get_total_priority(), 477)
