import os
import unittest
from pathlib import Path

from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy
from common.entities.base_entities.package import PackageType
from end_to_end.minimum_end_to_end import create_time_overlapping_dependent_graph_model, calc_assignment
from end_to_end.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput


class BasicMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategory.dict_to_obj(SupplierCategory.json_to_dict(
            Path('end_to_end/tests/jsons/test_supplier_category.json')))
        cls.empty_drone_delivery_board = \
            generate_empty_delivery_board(drone_set_properties=[BasicMinimumEnd2End._create_simple_drone_set_properties()],
                                          max_route_time_entire_board=400,
                                          velocity_entire_board=10)
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('end_to_end/tests/jsons/test_min_e2e_config.json')))

    @classmethod
    def _create_simple_drone_set_properties(cls):
        return DroneSetProperties(drone_type=DroneType.drone_type_1,
                                  drone_formation_policy=DroneFormationTypePolicy(
                                      {DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0}),
                                  package_configuration_policy=PackageConfigurationPolicy(
                                      {PackageConfiguration.LARGE_X2: 0.4, PackageConfiguration.MEDIUM_X4: 0.2,
                                       PackageConfiguration.SMALL_X8: 0.2, PackageConfiguration.TINY_X16: 0.2}),
                                  start_loading_dock=DroneLoadingDock
                                  drone_amount=30)

    def test_create_graph_model(self):
        operational_graph = create_time_overlapping_dependent_graph_model(self.supplier_category)
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    @unittest.skipIf(os.environ.get('NO_SLOW_TESTS', False), 'slow tests')
    def test_calc_assignment(self):
        operational_graph = create_time_overlapping_dependent_graph_model(self.supplier_category)
        matcher_input = MatcherInput(graph=operational_graph,
                                     empty_board=self.empty_drone_delivery_board,
                                     config=self.matcher_config)

        delivery_board = calc_assignment(matcher_input=matcher_input)
        self.assertEqual(4, len(delivery_board.unmatched_delivery_requests))
        amount_per_package_type = delivery_board.get_total_amount_per_package_type()
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.TINY), 1)
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.MEDIUM), 1)
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.LARGE), 4)
        self.assertEqual(delivery_board.get_total_priority(), 477)
