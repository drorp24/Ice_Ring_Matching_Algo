from dataclasses import dataclass

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone import DroneType, PackageConfigurations
from common.entities.base_entities.drone_formation import DroneFormationType


@dataclass
class DroneFormationTypePolicy:
    formation_type_policy: {DroneFormationType, float}


@dataclass
class PackageConfigurationsPolicy:
    package_configurations_policy: {PackageConfigurations, float}


@dataclass
class DroneSetProperties(JsonableBaseEntity):
    drone_type: DroneType
    drone_formation_policy: DroneFormationTypePolicy
    package_configuration_policy: PackageConfigurationsPolicy
    drone_amount: int

    @classmethod
    def dict_to_obj(cls, dict_input):
        DroneSetProperties()