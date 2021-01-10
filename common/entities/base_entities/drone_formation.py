from enum import Enum, auto
from enum import IntEnum
from functools import lru_cache

from common.entities.base_entities.drone import DroneConfiguration, PlatformType, Configurations, \
    DroneConfigurations, PackageTypeAmounts
from common.entities.base_entities.package import PackageType


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

    def get_package_type_amount(self, package_type: PackageType) -> int:
        return self.size * self._drone_configuration.package_type_map.get_package_type_amount(package_type)

    def get_package_type_amounts(self) -> PackageTypeAmounts:
        return PackageTypeAmounts(
            list(map(lambda configuration_amounts:
                     configuration_amounts * self._size,
                     self._drone_configuration.package_type_map.get_package_type_amounts())))

    def get_package_type_formation(self) -> PackageType:
        package_type_amounts = self._drone_configuration.package_type_map.get_package_type_amounts()
        package_type_indexes = [pt_index for pt_index, pt_exist in enumerate(package_type_amounts) if pt_exist > 0]
        if len(package_type_indexes) != 1:
            raise TypeError(f"The drone formation should has only one package type")
        return self.get_package_types()[package_type_indexes[0]]

    @property
    @lru_cache()
    def max_route_times_in_minutes(self) -> int:
        # TODO: Change to real endurance
        return self.get_platform_type().value * 100

    def __hash__(self):
        return hash((self._size, self._drone_configuration))


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
