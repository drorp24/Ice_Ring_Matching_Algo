from dataclasses import dataclass

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType


@dataclass
class DroneFormationTypePolicy(JsonableBaseEntity):
    _formation_type_policy: {DroneFormationType, float}

    @property
    def policy(self):
        return self._formation_type_policy

    @classmethod
    def dict_to_obj(cls, dict_input):
        return DroneFormationTypePolicy(
            {DroneFormationType[ftp[0]]: ftp[1] for ftp in dict_input['policy'].items()})

    def __dict__(self):
        return {'__class__': self.__class__.__name__,
                'policy': {pcp[0].name: pcp[1] for pcp in
                           self._formation_type_policy.items()}}


@dataclass
class PackageConfigurationPolicy(JsonableBaseEntity):
    _package_configuration_policy: {PackageConfiguration, float}

    @property
    def policy(self):
        return self._package_configuration_policy

    def get_configurations(self) -> [PackageConfiguration]:
        return list(self.policy.keys())

    def get_probabilities(self):
        return list(self.policy.values())

    def get_amount(self):
        return len(self.get_configurations())

    @classmethod
    def dict_to_obj(cls, dict_input):
        return PackageConfigurationPolicy(
            {PackageConfiguration[pcp[0]]: pcp[1] for pcp in dict_input['policy'].items()})

    def __dict__(self):
        return {'__class__': self.__class__.__name__,
                'policy': {pcp[0].name: pcp[1] for pcp in
                           self._package_configuration_policy.items()}}


@dataclass
class DroneSetProperties(JsonableBaseEntity):
    _drone_type: DroneType
    _drone_formation_policy: DroneFormationTypePolicy
    _package_configuration_policy: PackageConfigurationPolicy
    _drone_amount: int

    @property
    def drone_type(self) -> DroneType:
        return self._drone_type

    @property
    def drone_formation_policy(self) -> DroneFormationTypePolicy:
        return self._drone_formation_policy

    @property
    def package_configuration_policy(self) -> PackageConfigurationPolicy:
        return self._package_configuration_policy

    @property
    def drone_amount(self) -> int:
        return self._drone_amount

    @classmethod
    def dict_to_obj(cls, dict_input):
        return DroneSetProperties(
            _drone_type=DroneType.dict_to_obj(dict_input['drone_type']),
            _drone_formation_policy=DroneFormationTypePolicy.dict_to_obj(dict_input['drone_formation_policy']),
            _package_configuration_policy= \
                PackageConfigurationPolicy.dict_to_obj(dict_input['package_configuration_policy']),
            _drone_amount=dict_input['drone_amount']
        )
