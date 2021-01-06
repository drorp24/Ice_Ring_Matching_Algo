from enum import Enum, auto
from enum import IntEnum

from common.entities.base_entities.drone import DronePackageConfiguration, DroneType, PackageConfigurations, \
    DroneConfigurations
from common.entities.base_entities.package import PackageType


class DroneFormationType(IntEnum):
    PAIR = 2
    QUAD = 4

    def get_amount_of_drones(self):
        return self.value


class DroneFormation:

    def __init__(self, formation_size: DroneFormationType, drone_configuration: DronePackageConfiguration):
        self._size = formation_size
        self._drone_configuration = drone_configuration

    @property
    def size(self) -> DroneFormationType:
        return self._size

    @property
    def drone_configuration(self) -> DronePackageConfiguration:
        return self._drone_configuration

    def get_platform_type(self) -> DroneType:
        return self._drone_configuration.get_platform_type()

    def get_package_types(self) -> [PackageType]:
        return self._drone_configuration.package_type_map.get_package_types()

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self._drone_configuration.package_type_map.get_package_type_volume(package_type)

    def get_package_type_volumes(self) -> [int]:
        return self._drone_configuration.package_type_map.get_package_types_volumes()


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class PackageConfigurationOptions(AutoName):
    LARGE_PACKAGES = auto()
    MEDIUM_PACKAGES = auto()
    SMALL_PACKAGES = auto()
    TINY_PACKAGES = auto()


class DroneFormationOptions:
    drone_configurations_map: {PackageConfigurationOptions: [DronePackageConfiguration]} = {
        PackageConfigurationOptions.LARGE_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfigurations.LARGE_X2),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfigurations.LARGE_X4)],
        PackageConfigurationOptions.MEDIUM_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfigurations.MEDIUM_X4),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfigurations.MEDIUM_X8)],
        PackageConfigurationOptions.SMALL_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfigurations.SMALL_X8),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfigurations.SMALL_X16)],
        PackageConfigurationOptions.TINY_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfigurations.TINY_X16),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfigurations.TINY_X32)],
    }

    @classmethod
    def add_drone_configuration_option(cls, formation_option: PackageConfigurationOptions,
                                       drone_configurations: [DronePackageConfiguration]):
        cls.drone_configurations_map[formation_option] = drone_configurations

    @classmethod
    def _get_drone_configuration(cls, formation_option: PackageConfigurationOptions,
                                 platform_type: DroneType) -> DronePackageConfiguration:
        drone_configurations = cls.drone_configurations_map[formation_option]
        for drone_configuration in drone_configurations:
            if drone_configuration.get_platform_type() == platform_type:
                return drone_configuration

    @classmethod
    def get_drone_formation(cls, formation_size: DroneFormationType, formation_option: PackageConfigurationOptions,
                            platform_type: DroneType) -> DroneFormation:
        drone_configuration = cls._get_drone_configuration(formation_option, platform_type)
        return DroneFormation(formation_size, drone_configuration)

    @classmethod
    def get_formation_option(cls, configuration: PackageConfigurations, platform_type: DroneType):
        drone_configuration = DroneConfigurations.get_drone_configuration(platform_type, configuration)
        for formation_option, drone_configurations in cls.drone_configurations_map.items():
            for drone_conf in drone_configurations:
                if drone_configuration == drone_conf:
                    return formation_option


class DroneFormations:
    drone_formations_map: {PackageConfigurationOptions: {DroneFormationType: {DroneType: DroneFormation}}} = {
        formation_option: {
            formation_size:
                {
                    platform_type:
                        DroneFormationOptions.get_drone_formation(
                            formation_size,
                            formation_option,
                            platform_type)
                    for
                    platform_type
                    in
                    DroneType}
            for formation_size
            in DroneFormationType}
        for formation_option in
        PackageConfigurationOptions}

    @classmethod
    def get_drone_formation(cls, formation_size: DroneFormationType, formation_option: PackageConfigurationOptions,
                            platform_type: DroneType) -> DroneFormation:
        return cls.drone_formations_map[formation_option][formation_size][platform_type]

    @classmethod
    def create_default_drone_formations_amounts(cls, platform_type: DroneType) -> {DroneFormation: int}:
        formation_amounts = {}
        for formation_option in PackageConfigurationOptions:
            for formation_size in DroneFormationType:
                formation_amounts[cls.drone_formations_map[formation_option][formation_size][platform_type]] = 0
        return formation_amounts
