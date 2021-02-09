from __future__ import annotations
from enum import Enum

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.package import PackageType


class DroneType(Enum):
    drone_type_1 = 4
    drone_type_2 = 6

    @classmethod
    def dict_to_obj(cls, input_dict):
        split_name = input_dict['__enum__'].split('.')
        assert (split_name[0] == 'DroneType')
        return DroneType[split_name[1]]

    def __dict__(self):
        return {'__enum__': str(self)}

    def __repr__(self):
        return 'DroneType: ' + str(self.__dict__())


class PackageTypeAmountMap(JsonableBaseEntity):

    def __init__(self, package_types_amounts: {PackageType: int}):
        self._package_type_to_amounts = package_types_amounts

    @property
    def package_type_to_amounts(self) -> dict:
        return self._package_type_to_amounts

    @classmethod
    def dict_to_obj(cls, dict_input):
        return PackageTypeAmountMap({PackageType[package_type_amount[0]]: package_type_amount[1]
                                     for package_type_amount in dict_input['package_type_to_amounts'].items()})

    def add_to_map(self, other_package_types_amounts: PackageTypeAmountMap):
        other_amounts = other_package_types_amounts.package_type_to_amounts
        for key, val in other_amounts.items():
            if key not in self._package_type_to_amounts.keys():
                self._package_type_to_amounts[key] = 0
            self._package_type_to_amounts[key] += val

    def get_package_types(self) -> [PackageType]:
        return list(self._package_type_to_amounts.keys())

    def get_package_type_amount(self, package_type: PackageType) -> int:
        return self.package_type_to_amounts.get(package_type, 0)

    def get_package_type_amounts(self) -> [int]:
        return list(self.package_type_to_amounts.values())

    def __hash__(self):
        return hash(tuple(sorted(self._package_type_to_amounts.items())))

    def __str__(self):
        return '[' + ' '.join(
            map(lambda item: str(item[0]).split('.')[1] + ':' + str(item[1]),
                self.package_type_to_amounts.items())) + ']'

    def __eq__(self, other):
        return self.package_type_to_amounts == other.package_type_to_amounts

    def calc_total_weight(self) -> float:
        return sum(list([pta[0].calc_weight() * pta[1] for pta in list(self._package_type_to_amounts.items())]))

    def __lt__(self, other):
        return self.calc_total_weight() < other.calc_total_weight()

    def __dict__(self):
        return {'__class__': self.__class__.__name__,
                'package_type_to_amounts': {package_type[0].name: package_type[1] for package_type in
                                            self.package_type_to_amounts.items()}}


class DronePackageConfiguration(JsonableBaseEntity):

    def __init__(self, drone_type: DroneType, package_type_map: PackageTypeAmountMap):
        self._drone_type = drone_type
        self._package_type_map = package_type_map

    @property
    def drone_type(self) -> DroneType:
        return self._drone_type

    @property
    def package_type_map(self) -> PackageTypeAmountMap:
        return self._package_type_map

    def get_package_type_amount(self, package_type: PackageType) -> int:
        return self.package_type_map.get_package_type_amount(package_type)

    def get_drone_type(self) -> DroneType:
        return self._drone_type

    def __hash__(self):
        return hash((self._drone_type, self.package_type_map))

    def __eq__(self, other):
        return self.drone_type == other.drone_type \
               and self.package_type_map == other.package_type_map

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DronePackageConfiguration(
            drone_type=DroneType.dict_to_obj(dict_input['drone_type']),
            package_type_map=PackageTypeAmountMap.dict_to_obj(dict_input['package_type_map']))


class PackageConfiguration(Enum):
    LARGE_X2 = PackageTypeAmountMap({PackageType.LARGE: 2})
    MEDIUM_X4 = PackageTypeAmountMap({PackageType.MEDIUM: 4})
    SMALL_X8 = PackageTypeAmountMap({PackageType.SMALL: 8})
    TINY_X16 = PackageTypeAmountMap({PackageType.TINY: 16})
    LARGE_X4 = PackageTypeAmountMap({PackageType.LARGE: 4})
    MEDIUM_X8 = PackageTypeAmountMap({PackageType.MEDIUM: 8})
    SMALL_X16 = PackageTypeAmountMap({PackageType.SMALL: 16})
    TINY_X32 = PackageTypeAmountMap({PackageType.TINY: 32})

    @classmethod
    def dict_to_obj(cls, input_dict):
        split_name = input_dict['__enum__'].split('.')
        assert (split_name[0] == 'PackageConfiguration')
        return DroneType[split_name[1]]

    def __dict__(self):
        return {'__enum__': str(self.__dict__())}

    def __repr__(self):
        return 'PackageConfiguration: ' + str(self.__dict__())

    def __lt__(self, other):
        return self.value.calc_total_weight() < other.value.calc_total_weight()


class DroneTypeToPackageConfigurationOptions:
    drone_configurations_map: {DroneType: [PackageConfiguration]} = \
        {DroneType.drone_type_1: [PackageConfiguration.LARGE_X2, PackageConfiguration.MEDIUM_X4,
                                  PackageConfiguration.SMALL_X8, PackageConfiguration.TINY_X16],
         DroneType.drone_type_2: [PackageConfiguration.LARGE_X4, PackageConfiguration.MEDIUM_X8,
                                  PackageConfiguration.SMALL_X16, PackageConfiguration.TINY_X32]}

    @classmethod
    def add_configuration_option(cls, configuration_option: {DroneType: [PackageConfiguration]}):
        for key in configuration_option:
            cls.drone_configurations_map[key] = configuration_option[key]

    @classmethod
    def get_drone_configuration(cls, drone_type: DroneType,
                                configuration: PackageConfiguration) -> DronePackageConfiguration:
        index = cls.drone_configurations_map[drone_type].index(configuration)
        return DronePackageConfiguration(drone_type, cls.drone_configurations_map[drone_type][index].value)


class DroneConfigurations:
    drone_configurations_map: {DroneType: {PackageConfiguration: DronePackageConfiguration}} = \
        {drone_type: {
            configuration: DroneTypeToPackageConfigurationOptions.get_drone_configuration(drone_type, configuration)
            for configuration in configurations}
            for drone_type, configurations in
            DroneTypeToPackageConfigurationOptions.drone_configurations_map.items()}

    @classmethod
    def get_drone_configuration(cls, drone_type: DroneType,
                                configuration: PackageConfiguration) -> DronePackageConfiguration:
        return cls.drone_configurations_map[drone_type][configuration]
