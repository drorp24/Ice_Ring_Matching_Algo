from enum import Enum, auto
from enum import IntEnum

from common.entities.drone import DroneConfiguration, PlatformType, Configurations, \
    DroneConfigurations
from common.entities.package import PackageType


class FormationSize(IntEnum):
    MINI = 2
    MEDIUM = 4


class DroneFormation:

    def __init__(self, formation_size: FormationSize, drone_configuration: DroneConfiguration):
        self._size = formation_size
        self._drone_configuration = drone_configuration

    @property
    def size(self) -> FormationSize:
        return self._size

    @property
    def drone_configuration(self) -> DroneConfiguration:
        return self._drone_configuration

    def get_platform_type(self) -> PlatformType:
        return self._drone_configuration.get_platform_type()

    def get_package_types(self) -> [PackageType]:
        return self._drone_configuration.package_type_map.get_package_types()

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self.size * self._drone_configuration.package_type_map.get_package_type_volume(package_type)

    def get_package_type_volumes(self) -> [int]:
        return self._drone_configuration.package_type_map.get_package_types_volumes()

    def get_package_type_formation(self) -> PackageType:
        package_type_volumes = self._drone_configuration.package_type_map.get_package_types_volumes()
        package_type_indexes = [pt_index for pt_index, pt_exist in enumerate(package_type_volumes) if pt_exist > 0]
        if len(package_type_indexes) != 1:
            raise TypeError(f"The drone formation should has only one package type")
        return self.get_package_types()[package_type_indexes[0]]


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class FormationOptions(AutoName):
    LARGE_PACKAGES = auto()
    MEDIUM_PACKAGES = auto()
    SMALL_PACKAGES = auto()
    TINY_PACKAGES = auto()


class DroneFormationOptions:
    drone_configurations_map: {FormationOptions: [DroneConfiguration]} = {
        FormationOptions.LARGE_PACKAGES: [
            DroneConfigurations.get_drone_configuration(PlatformType.platform_1, Configurations.LARGE_X2),
            DroneConfigurations.get_drone_configuration(PlatformType.platform_2, Configurations.LARGE_X4)],
        FormationOptions.MEDIUM_PACKAGES: [
            DroneConfigurations.get_drone_configuration(PlatformType.platform_1, Configurations.MEDIUM_X4),
            DroneConfigurations.get_drone_configuration(PlatformType.platform_2, Configurations.MEDIUM_X8)],
        FormationOptions.SMALL_PACKAGES: [
            DroneConfigurations.get_drone_configuration(PlatformType.platform_1, Configurations.SMALL_X8),
            DroneConfigurations.get_drone_configuration(PlatformType.platform_2, Configurations.SMALL_X16)],
        FormationOptions.TINY_PACKAGES: [
            DroneConfigurations.get_drone_configuration(PlatformType.platform_1, Configurations.TINY_X16),
            DroneConfigurations.get_drone_configuration(PlatformType.platform_2, Configurations.TINY_X32)],
    }

    @classmethod
    def add_drone_configuration_option(cls, formation_option: FormationOptions,
                                       drone_configurations: [DroneConfiguration]):
        cls.drone_configurations_map[formation_option] = drone_configurations

    @classmethod
    def _get_drone_configuration(cls, formation_option: FormationOptions,
                                 platform_type: PlatformType) -> DroneConfiguration:
        drone_configurations = cls.drone_configurations_map[formation_option]
        for drone_configuration in drone_configurations:
            if drone_configuration.get_platform_type() == platform_type:
                return drone_configuration

    @classmethod
    def get_drone_formation(cls, formation_size: FormationSize, formation_option: FormationOptions,
                            platform_type: PlatformType) -> DroneFormation:
        drone_configuration = cls._get_drone_configuration(formation_option, platform_type)
        return DroneFormation(formation_size, drone_configuration)

    @classmethod
    def get_formation_option(cls, configuration: Configurations, platform_type: PlatformType):
        drone_configuration = DroneConfigurations.get_drone_configuration(platform_type, configuration)
        for formation_option, drone_configurations in cls.drone_configurations_map.items():
            for drone_conf in drone_configurations:
                if drone_configuration == drone_conf:
                    return formation_option


class DroneFormations:
    drone_formations_map: {FormationOptions: {FormationSize: {PlatformType: DroneFormation}}} = {formation_option: {
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
                PlatformType}
        for formation_size
        in FormationSize}
        for formation_option in
        FormationOptions}

    @classmethod
    def get_drone_formation(cls, formation_size: FormationSize, formation_option: FormationOptions,
                            platform_type: PlatformType) -> DroneFormation:
        return cls.drone_formations_map[formation_option][formation_size][platform_type]

    @classmethod
    def create_default_drone_formations_amounts(cls, platform_type: PlatformType) -> {DroneFormation: int}:
        formation_amounts = {}
        for formation_option in FormationOptions:
            for formation_size in FormationSize:
                formation_amounts[cls.drone_formations_map[formation_option][formation_size][platform_type]] = 0
        return formation_amounts
