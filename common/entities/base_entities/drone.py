from enum import Enum

from common.entities.base_entities.package import PackageType
from common.entities.base_entities.base_entity import JsonableBaseEntity

class PlatformType(JsonableBaseEntity, Enum):
    platform_1 = 4
    platform_2 = 6

    @classmethod
    def dict_to_obj(cls, dict_input):
        return PlatformType[dict_input['name']]


class PackageTypesVolumeMap:

    def __init__(self, packages_types_volume: [int]):
        self._dict = {}
        keys = [package_type for package_type in PackageType]
        for count, key in enumerate(keys):
            self._dict[key] = packages_types_volume[count]

    @property
    def dict(self) -> dict:
        return self._dict

    def get_package_types(self) -> [PackageType]:
        return list(self._dict.keys())

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self._dict[package_type]

    def get_package_types_volumes(self) -> [int]:
        return list(self._dict.values())

    def __str__(self):
        return '[' + ' '.join(
            map(lambda item: str(item[0].name) + ':' + str(item[1]), self.dict.items())) + ']'


class DroneConfiguration:

    def __init__(self, platform_type: PlatformType, package_types_map: PackageTypesVolumeMap):
        self._platform_type = platform_type
        self._package_types_map = package_types_map

    @property
    def platform_type(self) -> PlatformType:
        return self._platform_type

    @property
    def package_type_map(self) -> PackageTypesVolumeMap:
        return self._package_types_map

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self._package_types_map.get_package_type_volume(package_type)

    def get_platform_type(self) -> PlatformType:
        return self._platform_type


class Configurations(Enum):
    LARGE_X2 = PackageTypesVolumeMap([0, 0, 0, 2])
    MEDIUM_X4 = PackageTypesVolumeMap([0, 0, 4, 0])
    SMALL_X8 = PackageTypesVolumeMap([0, 8, 0, 0])
    TINY_X16 = PackageTypesVolumeMap([16, 0, 0, 0])
    LARGE_X4 = PackageTypesVolumeMap([0, 0, 0, 4])
    MEDIUM_X8 = PackageTypesVolumeMap([0, 0, 8, 0])
    SMALL_X16 = PackageTypesVolumeMap([0, 16, 0, 0])
    TINY_X32 = PackageTypesVolumeMap([32, 0, 0, 0])


class DroneConfigurationOptions:
    drone_configurations_map: {PlatformType: [Configurations]} = \
        {PlatformType.platform_1: [Configurations.LARGE_X2, Configurations.MEDIUM_X4, Configurations.SMALL_X8,
                                   Configurations.TINY_X16],
         PlatformType.platform_2: [Configurations.LARGE_X4, Configurations.MEDIUM_X8, Configurations.SMALL_X16,
                                   Configurations.TINY_X32]}

    @classmethod
    def add_configuration_option(cls, configuration_option: {PlatformType: [Configurations]}):
        for key in configuration_option:
            cls.drone_configurations_map[key] = configuration_option[key]

    @classmethod
    def get_drone_configuration(cls, platform_type: PlatformType, configuration: Configurations) -> DroneConfiguration:
        index = cls.drone_configurations_map[platform_type].index(configuration)
        return DroneConfiguration(platform_type, cls.drone_configurations_map[platform_type][index].value)


class DroneConfigurations:
    drone_configurations_map: {PlatformType: {Configurations: DroneConfiguration}} = \
        {platform_type: {configuration: DroneConfigurationOptions.get_drone_configuration(platform_type, configuration)
                         for configuration in configurations}
         for platform_type, configurations in DroneConfigurationOptions.drone_configurations_map.items()}

    @classmethod
    def get_drone_configuration(cls, platform_type: PlatformType, configuration: Configurations) -> DroneConfiguration:
        return cls.drone_configurations_map[platform_type][configuration]
