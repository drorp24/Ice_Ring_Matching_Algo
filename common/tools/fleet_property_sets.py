from dataclasses import dataclass
from common.entities.drone import PlatformType, Configurations
from common.entities.drone_formation import FormationSize, DroneFormationOptions, DroneFormation


@dataclass
class PlatformsFleetPropertySet:
    platforms_fleet: {PlatformType: int}


@dataclass
class PlatformFormationsSizePolicyPropertySet:
    formation_size_policy: {FormationSize, float}


@dataclass
class PlatformConfigurationsPolicyPropertySet:
    configurations_policy: {Configurations, float}


@dataclass
class PlatformPropertySet:
    platform_type: PlatformType
    configuration_policy: PlatformConfigurationsPolicyPropertySet
    formation_policy: PlatformFormationsSizePolicyPropertySet
    size: int

