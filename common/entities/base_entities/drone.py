from __future__ import annotations

from copy import copy
from enum import Enum

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.package import PackageType


class DroneType(Enum):
    drone_type_1 = 4
    drone_type_2 = 6
    drone_type_3 = 10
    drone_type_4 = 12

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

    def repr_as_lists(self) -> dict:
        return {"package_types": list(pt.name for pt in self._package_type_to_amounts.keys()),
                "amounts": list(amount for amount in self._package_type_to_amounts.values())}

    def add_packages_to_map(self, other_package_types_amounts: PackageTypeAmountMap):
        other_amounts = other_package_types_amounts.package_type_to_amounts
        for key, val in other_amounts.items():
            if key not in self._package_type_to_amounts.keys():
                self._package_type_to_amounts[key] = 0
            self._package_type_to_amounts[key] += val

    def get_package_types(self) -> [PackageType]:
        return list(self._package_type_to_amounts.keys())

    def get_active_package_types(self) -> [PackageType]:
        return dict(filter(lambda elem: elem[1] != 0, self._package_type_to_amounts.items()))

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

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        new_copy = PackageTypeAmountMap(copy(self._package_type_to_amounts))
        memodict[id(self)] = new_copy
        return new_copy


class DronePackageConfiguration(JsonableBaseEntity):

    def __init__(self, drone_type: DroneType, package_type_map: PackageTypeAmountMap, max_session_time: int):
        self._drone_type = drone_type
        self._package_type_map = package_type_map
        self._max_session_time = max_session_time

    @property
    def drone_type(self) -> DroneType:
        return self._drone_type

    @property
    def package_type_map(self) -> PackageTypeAmountMap:
        return self._package_type_map

    @property
    def max_session_time(self) -> int:
        return self._max_session_time

    @max_session_time.setter
    def max_session_time(self, max_session_time: int):
        self._max_session_time = max_session_time

    def get_package_type_amount(self, package_type: PackageType) -> int:
        return self.package_type_map.get_package_type_amount(package_type)

    def get_drone_type(self) -> DroneType:
        return self._drone_type

    def __hash__(self):
        return hash((self._drone_type, self.package_type_map))

    def __eq__(self, other):
        return self.drone_type == other.drone_type \
               and self.package_type_map == other.package_type_map

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        new_copy = DronePackageConfiguration(self._drone_type, self.package_type_map)
        memodict[id(self)] = new_copy
        return new_copy

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DronePackageConfiguration(
            drone_type=DroneType.dict_to_obj(dict_input['drone_type']),
            package_type_map=PackageTypeAmountMap.dict_to_obj(dict_input['package_type_map']),
            max_session_time=dict_input['max_session_time'])


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
        return {'__enum__': str(self)}

    def __repr__(self):
        return 'PackageConfiguration: ' + str(self.__dict__())

    def __lt__(self, other):
        return self.value.calc_total_weight() < other.value.calc_total_weight()


class DroneTypeToPackageConfigurationOptions:
    drone_configurations_map: {DroneType: {PackageConfiguration: int}} = \
        {DroneType.drone_type_1: {PackageConfiguration.LARGE_X2: 400,
                                  PackageConfiguration.MEDIUM_X4: 400,
                                  PackageConfiguration.SMALL_X8: 400,
                                  PackageConfiguration.TINY_X16: 400},
         DroneType.drone_type_2: {PackageConfiguration.LARGE_X4: 400,
                                  PackageConfiguration.MEDIUM_X8: 400,
                                  PackageConfiguration.SMALL_X16: 400,
                                  PackageConfiguration.TINY_X32: 400},
         DroneType.drone_type_3: {PackageConfiguration.LARGE_X2: 400,
                                  PackageConfiguration.MEDIUM_X4: 400,
                                  PackageConfiguration.SMALL_X8: 400,
                                  PackageConfiguration.TINY_X16: 400},
         DroneType.drone_type_4: {PackageConfiguration.LARGE_X2: 400,
                                  PackageConfiguration.MEDIUM_X4: 400,
                                  PackageConfiguration.SMALL_X8: 400,
                                  PackageConfiguration.TINY_X16: 400}}

    @classmethod
    def add_configuration_option(cls, configuration_option: {DroneType: {PackageConfiguration: int}}):
        for key in configuration_option:
            cls.drone_configurations_map[key].update(configuration_option[key])

    @classmethod
    def get_drone_configuration(cls, drone_type: DroneType,
                                configuration: PackageConfiguration) -> DronePackageConfiguration:
        return DronePackageConfiguration(drone_type=drone_type, package_type_map=configuration.value,
                                         max_session_time=cls.drone_configurations_map[drone_type][configuration])

    @classmethod
    def update_max_session_time(cls, drone_type: DroneType,
                                configuration: PackageConfiguration,
                                max_session_time: int):
        cls.drone_configurations_map[drone_type][configuration] = max_session_time


class DroneConfigurations:
    @classmethod
    def get_drone_configuration(cls, drone_type: DroneType,
                                configuration: PackageConfiguration) -> DronePackageConfiguration:
        return DroneTypeToPackageConfigurationOptions.get_drone_configuration(drone_type=drone_type,
                                                                              configuration=configuration)
