from dataclasses import dataclass

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone import DroneType, PackageConfiguration
from common.entities.base_entities.drone_formation import DroneFormationType


@dataclass
class DroneFormationTypePolicy(JsonableBaseEntity):
    policy: {DroneFormationType, float}

    @classmethod
    def dict_to_obj(cls, dict_input):
        return DroneFormationTypePolicy(
            {DroneFormationType[ftp[0]]: ftp[1] for ftp in dict_input['policy'].items()})

    def __dict__(self):
        return {'__class__': self.__class__.__name__,
                'policy': {pcp[0].name: pcp[1] for pcp in
                           self.policy.items()}}

    def __hash__(self):
        return hash(tuple(self.policy))


@dataclass
class PackageConfigurationPolicy(JsonableBaseEntity):
    policy: {PackageConfiguration, float}

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
                           self.policy.items()}}


@dataclass
class DroneSetProperties(JsonableBaseEntity):

    def __init__(self, drone_type: DroneType, drone_formation_policy: DroneFormationTypePolicy,
                 package_configuration_policy: PackageConfigurationPolicy, drone_amount: int):
        self._drone_type = drone_type
        self._drone_formation_policy = drone_formation_policy
        self._package_configuration_policy = package_configuration_policy
        self._drone_amount = drone_amount

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
            drone_type=DroneType.dict_to_obj(dict_input['drone_type']),
            drone_formation_policy=DroneFormationTypePolicy.dict_to_obj(dict_input['drone_formation_policy']),
            package_configuration_policy=PackageConfigurationPolicy.dict_to_obj(
                dict_input['package_configuration_policy']),
            drone_amount=dict_input['drone_amount']
        )
