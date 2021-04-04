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
    drone_type: DroneType
    drone_formation_policy: DroneFormationTypePolicy
    package_configuration_policy: PackageConfigurationPolicy
    drone_amount: int

    @classmethod
    def dict_to_obj(cls, dict_input):
        return DroneSetProperties(
            drone_type=DroneType.dict_to_obj(dict_input['drone_type']),
            drone_formation_policy=DroneFormationTypePolicy.dict_to_obj(dict_input['drone_formation_policy']),
            package_configuration_policy=PackageConfigurationPolicy.dict_to_obj(
                dict_input['package_configuration_policy']),
            drone_amount=dict_input['drone_amount']
        )

    def __eq__(self, other):
        return self.drone_type == other.drone_type \
               and self.drone_formation_policy == other.drone_formation_policy \
               and self.package_configuration_policy == other.package_configuration_policy \
               and self.drone_amount == other.drone_amount


@dataclass
class BoardLevelProperties(JsonableBaseEntity):
    max_route_time_entire_board: int = 400
    velocity_entire_board: float = 10.0

    @classmethod
    def dict_to_obj(cls, dict_input):
        return BoardLevelProperties(
            max_route_time_entire_board=dict_input['max_route_time_entire_board'],
            velocity_entire_board=dict_input['velocity_entire_board']
        )

    def __eq__(self, other):
        return self.max_route_time_entire_board == other.max_route_time_entire_board \
               and self.velocity_entire_board == other.velocity_entire_board
