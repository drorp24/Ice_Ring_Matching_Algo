import unittest
from pathlib import Path
from pprint import pprint
from random import Random
from typing import List
from common.entities.drone_formation import FormationSize
from common.entities.delivery_request import build_delivery_request_distribution, \
    DeliveryRequest
from common.entities.package import PackageDistribution, PackageType
from common.tools.empty_drone_delivery_board_generation import build_empty_drone_delivery_board
from common.tools.fleet_property_sets import *
from end_to_end.minimum_end_to_end import MinimumEnd2EndConfig, DataLoader, MinimumEnd2End
from end_to_end.scenario import ScenarioDistribution
from geometry.geo_distribution import NormalPointDistribution
from geometry.geo_factory import create_point_2d
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.operational.operational_drawer2d import add_operational_graph, add_delivery_request


def _create_delivery_request_distribution():
    package_distribution = create_single_package_distribution()
    delivery_request_distribution = build_delivery_request_distribution(
        package_type_distribution=package_distribution,
        relative_dr_location_distribution = NormalPointDistribution(create_point_2d(10,30), 10, 10))
    return delivery_request_distribution


def create_single_package_distribution():
    package_type_distribution_dict = {PackageType.LARGE.name:1}
    package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
    return package_distribution


def _create_empty_drone_delivery_board(
        formation_size_policy: dict = {FormationSize.MINI: 0.5, FormationSize.MEDIUM: 0.5},
        configurations_policy: dict = {Configurations.LARGE_X2: 1,
                                       Configurations.MEDIUM_X4: 0,
                                       Configurations.SMALL_X8: 0,
                                       Configurations.TINY_X16: 0}
        , platform_type: PlatformType = PlatformType.platform_1,
        size: int = 30):
    formation_size_property_set = PlatformFormationsSizePolicyPropertySet(formation_size_policy)
    configuration_policy_property_set = PlatformConfigurationsPolicyPropertySet(configurations_policy)
    platform_property_set = PlatformPropertySet(platform_type=platform_type,
                                                configuration_policy=configuration_policy_property_set,
                                                formation_policy=formation_size_property_set,
                                                size=size)
    return build_empty_drone_delivery_board(platform_property_set)


class BasicMinimumEnd2EndPresentation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scenario_distribution = ScenarioDistribution(
            delivery_requests_distribution=_create_delivery_request_distribution())
        cls.matcher_config = Path("end_to_end/tests/jsons/test_matcher_config.json")

    def test_small_scenario(self):
        empty_drone_delivery_board = _create_empty_drone_delivery_board(size=10)
        minimum_end_to_end = MinimumEnd2End(scenario=self.scenario_distribution.choose_rand(random = Random(10),amount=10),
                                            empty_drone_delivery_board=empty_drone_delivery_board)
        fully_connected_graph = minimum_end_to_end.create_fully_connected_graph_model()
        delivery_board = minimum_end_to_end.calc_assignment(fully_connected_graph, self.matcher_config)
        d = create_drawer_2d()
        # [add_delivery_request(d, dr) for dr in minimum_end_to_end.delivery_requests]
        add_operational_graph(d, fully_connected_graph)
        d.draw()
        print(delivery_board)
