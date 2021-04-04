import os
import unittest
from datetime import timedelta
from pathlib import Path

from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, DroneFormationTypePolicy, \
    PackageConfigurationPolicy
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeWindowExtension, TimeDeltaExtension
from common.entities.base_entities.tests.test_drone_delivery import ZERO_TIME
from end_to_end.arrival_envelope_minimum_end_to_end import create_time_overlapping_dependent_graph_model, calc_assignment
from end_to_end.supplier_category import SupplierCategory
from geometry.geo_factory import create_point_2d
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput


class BasicArrivalEnvelopeMinimumEnd2End(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategory.dict_to_obj(SupplierCategory.json_to_dict(
            Path('end_to_end/tests/jsons/test_supplier_category.json')))
        cls.empty_drone_delivery_board = \
            generate_empty_delivery_board(drone_set_properties=[BasicArrivalEnvelopeMinimumEnd2End._create_simple_drone_set_properties()],
                                          max_route_time_entire_board=400,
                                          velocity_entire_board=10)
        cls.matcher_config = MatcherConfig.dict_to_obj(
            MatcherConfig.json_to_dict(Path('end_to_end/tests/jsons/test_min_e2e_config.json')))

    @classmethod
    def _create_simple_drone_set_properties(cls):
        loading_dock = DroneLoadingDock(EntityID.generate_uuid(),
                                        DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 0)),
                                        DroneType.drone_type_1,
                                        TimeWindowExtension(
                                            since=ZERO_TIME,
                                            until=ZERO_TIME.add_time_delta(
                                                TimeDeltaExtension(timedelta(hours=5)))))
        return DroneSetProperties(drone_type=DroneType.drone_type_1,
                                  drone_formation_policy=DroneFormationTypePolicy(
                                      {DroneFormationType.PAIR: 1.0, DroneFormationType.QUAD: 0.0}),
                                  package_configuration_policy=PackageConfigurationPolicy(
                                      {PackageConfiguration.LARGE_X2: 0.6, PackageConfiguration.MEDIUM_X4: 0.2,
                                       PackageConfiguration.SMALL_X8: 0.2, PackageConfiguration.TINY_X16: 0.0}),
                                  start_loading_dock=loading_dock,
                                  end_loading_dock=loading_dock,
                                  drone_amount=30)

    def test_create_graph_model(self):
        operational_graph = create_time_overlapping_dependent_graph_model(self.supplier_category)
        self.assertEqual(len(operational_graph.nodes), 11)
        self.assertEqual(len(operational_graph.edges), 60)

    @unittest.skipIf(os.environ.get('NO_SLOW_TESTS', False), 'slow tests')
    def test_calc_assignment(self):
        operational_graph = create_time_overlapping_dependent_graph_model(supplier_category=self.supplier_category,
                                                                          edge_cost_factor=0.1,
                                                                          edge_travel_time_factor=0.1)
        matcher_input = MatcherInput(graph=operational_graph,
                                     empty_board=self.empty_drone_delivery_board,
                                     config=self.matcher_config)

        delivery_board = calc_assignment(matcher_input=matcher_input)
        self.assertEqual(len(delivery_board.unmatched_delivery_requests), 2)
        amount_per_package_type = delivery_board.get_total_amount_per_package_type()
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.SMALL), 0)
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.TINY), 0)
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.MEDIUM), 2)
        self.assertEqual(amount_per_package_type.get_package_type_amount(PackageType.LARGE), 6)
        self.assertEqual(delivery_board.get_total_priority(), 512)
