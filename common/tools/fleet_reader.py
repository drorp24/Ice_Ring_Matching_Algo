from common.tools.fleet_property_sets import *
from common.entities.drone import PlatformType, Configurations
from pathlib import Path
from common.utils.json_file_handler import create_dict_from_json
from enum import Enum


class FleetJsonReaderConsts(Enum):
    size = 0
    formation_policy = 1
    configuration_policy = 2


class FleetReader:
    def __init__(self, fleet_json_file_path: Path = 'Fleet.json'):
        self._file_path = fleet_json_file_path
        self._json_data = create_dict_from_json(self._file_path)

    def get_configurations_policy(self, platform: PlatformType) -> PlatformConfigurationsPolicyPropertySet:
        configurations_policy_json = self._json_data[platform.name][FleetJsonReaderConsts.configuration_policy.name]
        configurations = [Configurations[configuration] for configuration in configurations_policy_json.keys()]
        return PlatformConfigurationsPolicyPropertySet(dict(zip(configurations, configurations_policy_json.values())))

    def get_formation_size_policy(self, platform: PlatformType) -> PlatformFormationsSizePolicyPropertySet:
        formations_policy_json = self._json_data[platform.name][FleetJsonReaderConsts.formation_policy.name]
        formations = [FormationSize[formation] for formation in formations_policy_json.keys()]
        return PlatformFormationsSizePolicyPropertySet(dict(zip(formations, formations_policy_json.values())))

    def get_size(self, platform: PlatformType) -> int:
        return self._json_data[platform.name][FleetJsonReaderConsts.size.name]

    def get_platform_properties(self, platform: PlatformType) -> PlatformPropertySet:
        size = self.get_size(platform)
        platform_formation_policy_property_set = self.get_formation_size_policy(platform)
        platform_configurations_policy_property_set = self.get_configurations_policy(platform)
        return PlatformPropertySet(platform, platform_configurations_policy_property_set,
                                   platform_formation_policy_property_set, size)

    def get_platforms_properties(self) -> [PlatformPropertySet]:
        platform_names = list(self._json_data.keys())
        return [self.get_platform_properties(PlatformType[platform_name]) for platform_name in platform_names]


