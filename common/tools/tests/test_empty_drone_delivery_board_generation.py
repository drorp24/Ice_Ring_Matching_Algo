import unittest

from common.entities.base_entities.drone import PlatformType, Configurations
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormation, FormationSize
from common.tools.empty_drone_delivery_board_generation import generate_empty_delivery_board
from common.tools.fleet_property_sets import PlatformPropertySet, PlatformFormationsSizePolicyPropertySet, \
    PlatformConfigurationsPolicyPropertySet


class TestEmptyDroneDeliveryBoardGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.platform_property_set_1 = PlatformPropertySet(
            platform_type=PlatformType.platform_1,
            formation_policy=PlatformFormationsSizePolicyPropertySet(
                {FormationSize.MINI: 0.5,
                 FormationSize.MEDIUM: 0.5}),
            configuration_policy=PlatformConfigurationsPolicyPropertySet(
                {Configurations.LARGE_X2: 0.1,
                 Configurations.MEDIUM_X4: 0.4,
                 Configurations.SMALL_X8: 0.3,
                 Configurations.TINY_X16: 0.2}),
            size=30)

        cls.platform_property_set_2 = PlatformPropertySet(
            platform_type=PlatformType.platform_2,
            formation_policy=PlatformFormationsSizePolicyPropertySet(
                {FormationSize.MINI: 1.0,
                 FormationSize.MEDIUM: 0.0}),
            configuration_policy=PlatformConfigurationsPolicyPropertySet(
                {Configurations.LARGE_X4: 0.0,
                 Configurations.MEDIUM_X8: 0.4,
                 Configurations.SMALL_X16: 0.6,
                 Configurations.TINY_X32: 0.0}),
            size=30)

    def test_empty_drone_delivery_board(self):
        empty_drone_delivery_board = generate_empty_delivery_board(
            [self.platform_property_set_1, self.platform_property_set_2])
        self.assertIsInstance(empty_drone_delivery_board, EmptyDroneDeliveryBoard)
        self.assertEqual(len(empty_drone_delivery_board.empty_drone_deliveries), 24)
        self.assertIsInstance(empty_drone_delivery_board.empty_drone_deliveries[0].drone_formation, DroneFormation)
