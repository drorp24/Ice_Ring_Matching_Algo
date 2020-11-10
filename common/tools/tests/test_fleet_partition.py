from common.tools.fleet_reader import FleetReader
from common.entities.drone import PlatformType
from common.entities.drone_formation import FormationSize
from common.tools.fleet_partition import FleetPartition
import unittest
from common.tools.tests.path_utils import create_path_from_current_directory, Path


class FleetPartitionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fleet_reader = FleetReader(create_path_from_current_directory(Path('TestFleet.json')))

    def test_none_zero_formation_policy(self):
        platform_property_set = self.fleet_reader.get_platform_properties(PlatformType.platform_1)
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MINI], 5)
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MEDIUM], 5)

    def test_with_zero_formation_policy(self):
        platform_property_set = self.fleet_reader.get_platform_properties(PlatformType.platform_2)
        FleetPartition.extract_parameters(platform_property_set)
        formation_sizes_amounts = FleetPartition.solve()
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MINI], 15)
        self.assertEqual(formation_sizes_amounts.amounts[FormationSize.MEDIUM], 0)


