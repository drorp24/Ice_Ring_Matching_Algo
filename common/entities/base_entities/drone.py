from __future__ import annotations
from enum import Enum
from typing import Type

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


class _PackageTypeAmountMap(JsonableBaseEntity):

    def __init__(self, package_types_amounts: {str: int}):
        self._package_type_to_amounts = package_types_amounts

    @property
    def package_type_to_amounts(self) -> dict:
        return self._package_type_to_amounts

    @classmethod
    def dict_to_obj(cls, dict_input):
        return _PackageTypeAmountMap(dict_input['package_type_to_amounts'])

    def add_to_map(self, other_package_types_amounts: Type[_PackageTypeAmountMap]):
        other_amounts = other_package_types_amounts.package_type_to_amounts
        for key, val in other_amounts.items():
            if key not in self._package_type_to_amounts.keys():
                self._package_type_to_amounts[key] = 0
            self._package_type_to_amounts[key] += val

    def get_package_types(self) -> [PackageType]:
        return list(self._package_type_to_amounts.keys())

    def get_package_type_amount(self, package_type: PackageType) -> int:
        return self.package_type_to_amounts.get(package_type.name, 0)

    def get_package_type_amounts(self) -> [int]:
        return list(self.package_type_to_amounts.values())

    def __hash__(self):
        return hash(tuple(sorted(self._package_type_to_amounts.items())))

    def __str__(self):
        return '[' + ' '.join(
            map(lambda item: str(item[0]) + ':' + str(item[1]), self.package_type_to_amounts.items())) + ']'

    def __eq__(self, other):
        return self.package_type_to_amounts == other.package_type_to_amounts

    def calc_total_weight(self):
        return sum(list([PackageType[pta[0]].calc_weight() * pta[1] for pta in self._package_type_to_amounts.items()]))

    def __lt__(self, other):
        return self.calc_total_weight < other.calc_total_weight


class DronePackageConfiguration:

    def __init__(self, platform_type: DroneType, package_types_map: _PackageTypeAmountMap):
        self._platform_type = platform_type
        self._package_types_map = package_types_map

    def __hash__(self):
        return hash((self._platform_type, self._package_types_map))

    @property
    def platform_type(self) -> DroneType:
        return self._platform_type

    @property
    def package_type_map(self) -> _PackageTypeAmountMap:
        return self._package_types_map

    def get_package_type_amount(self, package_type: PackageType) -> int:
        return self._package_types_map.get_package_type_amount(package_type)

    def get_drone_type(self) -> DroneType:
        return self._platform_type


class PackageConfiguration(Enum):
    LARGE_X2 = _PackageTypeAmountMap({PackageType.LARGE.name: 2})
    MEDIUM_X4 = _PackageTypeAmountMap({PackageType.MEDIUM.name: 4})
    SMALL_X8 = _PackageTypeAmountMap({PackageType.SMALL.name: 8})
    TINY_X16 = _PackageTypeAmountMap({PackageType.TINY.name: 16})
    LARGE_X4 = _PackageTypeAmountMap({PackageType.LARGE.name: 4})
    MEDIUM_X8 = _PackageTypeAmountMap({PackageType.MEDIUM.name: 8})
    SMALL_X16 = _PackageTypeAmountMap({PackageType.SMALL.name: 16})
    TINY_X32 = _PackageTypeAmountMap({PackageType.TINY.name: 32})

    @classmethod
    def dict_to_obj(cls, input_dict):
        split_name = input_dict['__enum__'].split('.')
        assert (split_name[0] == 'PackageConfiguration')
        return DroneType[split_name[1]]

    def __dict__(self):
        return {'__enum__': str(self)}

    def __repr__(self):
        return 'PackageConfiguration: ' + str(self.__dict__())

    def __lt__(self, other):
        return self.value.calc_total_weight() < other.value.calc_total_weight()


class DroneTypeToPackageConfigurationOptions:
    drone_configurations_map: {DroneType: [PackageConfiguration]} = \
        {DroneType.drone_type_1: [PackageConfiguration.LARGE_X2, PackageConfiguration.MEDIUM_X4,
                                  PackageConfiguration.SMALL_X8,
                                  PackageConfiguration.TINY_X16],
         DroneType.drone_type_2: [PackageConfiguration.LARGE_X4, PackageConfiguration.MEDIUM_X8,
                                  PackageConfiguration.SMALL_X16,
                                  PackageConfiguration.TINY_X32]}

    @classmethod
    def add_configuration_option(cls, configuration_option: {DroneType: [PackageConfiguration]}):
        for key in configuration_option:
            cls.drone_configurations_map[key] = configuration_option[key]

    @classmethod
    def get_drone_configuration(cls, platform_type: DroneType,
                                configuration: PackageConfiguration) -> DronePackageConfiguration:
        index = cls.drone_configurations_map[platform_type].index(configuration)
        return DronePackageConfiguration(platform_type, cls.drone_configurations_map[platform_type][index].value)


class DroneConfigurations:
    drone_configurations_map: {DroneType: {PackageConfiguration: DronePackageConfiguration}} = \
        {platform_type: {
            configuration: DroneTypeToPackageConfigurationOptions.get_drone_configuration(platform_type, configuration)
            for configuration in configurations}
            for platform_type, configurations in
            DroneTypeToPackageConfigurationOptions.drone_configurations_map.items()}

    @classmethod
    def get_drone_configuration(cls, platform_type: DroneType,
                                configuration: PackageConfiguration) -> DronePackageConfiguration:
        return cls.drone_configurations_map[platform_type][configuration]
