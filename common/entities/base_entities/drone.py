from enum import Enum

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
        return 'PlatformType: ' + str(self.__dict__())


class _PackageTypesVolumeMap:

    def __init__(self, packages_types_volume: [int]):
        self._dict = {}
        keys = [package_type for package_type in PackageType]
        for count, key in enumerate(keys):
            self._dict[key] = packages_types_volume[count]

    @property
    def dict(self) -> dict:
        return self._dict

    def get_package_types(self) -> [PackageType]:
        return self._dict.keys()

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self._dict[package_type]

    def get_package_types_volumes(self) -> [int]:
        return self._dict.values()


class DronePackageConfiguration:

    def __init__(self, platform_type: DroneType, package_types_map: _PackageTypesVolumeMap):
        self._platform_type = platform_type
        self._package_types_map = package_types_map

    @property
    def platform_type(self) -> DroneType:
        return self._platform_type

    @property
    def package_type_map(self) -> _PackageTypesVolumeMap:
        return self._package_types_map

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self._package_types_map.get_package_type_volume(package_type)

    def get_platform_type(self) -> DroneType:
        return self._platform_type


class PackageConfigurations(Enum):
    LARGE_X2 = _PackageTypesVolumeMap([0, 0, 0, 2])
    MEDIUM_X4 = _PackageTypesVolumeMap([0, 0, 4, 0])
    SMALL_X8 = _PackageTypesVolumeMap([0, 8, 0, 0])
    TINY_X16 = _PackageTypesVolumeMap([16, 0, 0, 0])
    LARGE_X4 = _PackageTypesVolumeMap([0, 0, 0, 4])
    MEDIUM_X8 = _PackageTypesVolumeMap([0, 0, 8, 0])
    SMALL_X16 = _PackageTypesVolumeMap([0, 16, 0, 0])
    TINY_X32 = _PackageTypesVolumeMap([32, 0, 0, 0])


class DroneTypeToPackageConfigurationOptions:
    drone_configurations_map: {DroneType: [PackageConfigurations]} = \
        {DroneType.drone_type_1: [PackageConfigurations.LARGE_X2, PackageConfigurations.MEDIUM_X4, PackageConfigurations.SMALL_X8,
                                  PackageConfigurations.TINY_X16],
         DroneType.drone_type_2: [PackageConfigurations.LARGE_X4, PackageConfigurations.MEDIUM_X8, PackageConfigurations.SMALL_X16,
                                  PackageConfigurations.TINY_X32]}

    @classmethod
    def add_configuration_option(cls, configuration_option: {DroneType: [PackageConfigurations]}):
        for key in configuration_option:
            cls.drone_configurations_map[key] = configuration_option[key]

    @classmethod
    def get_drone_configuration(cls, platform_type: DroneType, configuration: PackageConfigurations) -> DronePackageConfiguration:
        index = cls.drone_configurations_map[platform_type].index(configuration)
        return DronePackageConfiguration(platform_type, cls.drone_configurations_map[platform_type][index].value)


class DroneConfigurations:
    drone_configurations_map: {DroneType: {PackageConfigurations: DronePackageConfiguration}} = \
        {platform_type: {configuration: DroneTypeToPackageConfigurationOptions.get_drone_configuration(platform_type, configuration)
                         for configuration in configurations}
         for platform_type, configurations in DroneTypeToPackageConfigurationOptions.drone_configurations_map.items()}

    @classmethod
    def get_drone_configuration(cls, platform_type: DroneType, configuration: PackageConfigurations) -> DronePackageConfiguration:
        return cls.drone_configurations_map[platform_type][configuration]
