from __future__ import annotations
from enum import Enum, auto
from functools import lru_cache

from common.entities.base_entities.drone import DronePackageConfiguration, PackageConfiguration, PackageTypeAmountMap
from common.entities.base_entities.drone import DroneType, DroneConfigurations
from common.entities.base_entities.package import PackageType


class DroneFormationType(Enum):
    PAIR = 2
    QUAD = 4

    def get_amount_of_drones(self):
        return self.value

    @classmethod
    def dict_to_obj(cls, input_dict):
        split_name = input_dict['__enum__'].split('.')
        assert (split_name[0] == 'DroneFormationType')
        return DroneFormationType[split_name[1]]

    def __dict__(self):
        return {'__enum__': str(self)}

    def __repr__(self):
        return 'DroneFormationType: ' + str(self.__dict__())

    def __eq__(self, other: DroneFormationType):
        return self.name == other.name and self.value == other.value

    def __hash__(self):
        return hash(tuple((self.name, self.value)))

    def __lt__(self, other):
        return self.value < other.value


class DroneFormation:

    def __init__(self, drone_formation_type: DroneFormationType, package_configuration: DronePackageConfiguration):
        self._drone_formation_type = drone_formation_type
        self._package_configuration = package_configuration

    @property
    def drone_formation_type(self) -> DroneFormationType:
        return self._drone_formation_type

    @property
    def drone_configuration(self) -> DronePackageConfiguration:
        return self._package_configuration

    @property
    @lru_cache()
    def max_route_times_in_minutes(self) -> int:
        # TODO: Change to real endurance
        return self.get_drone_type().value * 100

    def get_drone_type(self) -> DroneType:
        return self._package_configuration.get_drone_type()

    def get_package_type_amount(self, package_type: PackageType) -> int:
        return self.drone_formation_type.get_amount_of_drones() * \
               self._package_configuration.get_package_type_amount(package_type)

    def get_package_type_amount_map(self) -> PackageTypeAmountMap:
        amount_per_package_type = PackageTypeAmountMap({package: 0 for package in PackageType})
        extracted_package_type_amounts = PackageTypeAmountMap({
            package_type_name: package_amount * self.drone_formation_type.get_amount_of_drones() for
            package_type_name, package_amount in
            self._package_configuration.package_type_map.package_type_to_amounts.items()})
        amount_per_package_type.add_to_map(extracted_package_type_amounts)
        return amount_per_package_type

    def get_package_type(self) -> PackageType:
        formation_package_type = None
        package_type_amount_map = self._package_configuration.package_type_map
        for package_type in PackageType:
            if package_type_amount_map.get_package_type_amount(package_type) > 0:
                if formation_package_type is not None:
                    raise TypeError(f"Drone formation supports only one package type")
                formation_package_type = package_type
        return formation_package_type

    def __hash__(self):
        return hash((self._drone_formation_type, self._package_configuration))


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class PackageConfigurationOption(AutoName):
    LARGE_PACKAGES = auto()
    MEDIUM_PACKAGES = auto()
    SMALL_PACKAGES = auto()
    TINY_PACKAGES = auto()


class DroneTypeToPackageConfigurationOption:
    drone_configurations_map: {PackageConfigurationOption: [DronePackageConfiguration]} = {
        PackageConfigurationOption.LARGE_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfiguration.LARGE_X2),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfiguration.LARGE_X4)],
        PackageConfigurationOption.MEDIUM_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfiguration.MEDIUM_X4),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfiguration.MEDIUM_X8)],
        PackageConfigurationOption.SMALL_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfiguration.SMALL_X8),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfiguration.SMALL_X16)],
        PackageConfigurationOption.TINY_PACKAGES: [
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_1, PackageConfiguration.TINY_X16),
            DroneConfigurations.get_drone_configuration(DroneType.drone_type_2, PackageConfiguration.TINY_X32)],
    }

    @classmethod
    def add_drone_configuration_option(cls, formation_option: PackageConfigurationOption,
                                       drone_configurations: [DronePackageConfiguration]):
        cls.drone_configurations_map[formation_option] = drone_configurations

    @classmethod
    def _get_drone_configuration(cls, formation_option: PackageConfigurationOption,
                                 drone_type: DroneType) -> DronePackageConfiguration:
        drone_configurations = cls.drone_configurations_map[formation_option]
        for drone_configuration in drone_configurations:
            if drone_configuration.get_drone_type() == drone_type:
                return drone_configuration
        raise NoDronePackageConfigurationFoundException()

    @classmethod
    def get_drone_formation(cls, formation_type: DroneFormationType, formation_option: PackageConfigurationOption,
                            drone_type: DroneType) -> DroneFormation:
        drone_configuration = cls._get_drone_configuration(formation_option, drone_type)
        return DroneFormation(formation_type, drone_configuration)

    @classmethod
    def get_formation_option(cls, configuration: PackageConfiguration, drone_type: DroneType):
        drone_configuration = DroneConfigurations.get_drone_configuration(drone_type, configuration)
        for formation_option, drone_configurations in cls.drone_configurations_map.items():
            for drone_conf in drone_configurations:
                if drone_configuration == drone_conf:
                    return formation_option
        raise NoFormationOptionFoundException()


class DroneFormations:
    drone_formations_map: {PackageConfigurationOption: {DroneFormationType: {DroneType: DroneFormation}}} = {
        package_configuration_options: {
            drone_formation_type: {
                drone_type:
                    DroneTypeToPackageConfigurationOption.get_drone_formation(
                        drone_formation_type, package_configuration_options, drone_type)
                for drone_type in DroneType}
            for drone_formation_type in DroneFormationType}
        for package_configuration_options in PackageConfigurationOption}

    @classmethod
    def get_drone_formation(cls, formation_type: DroneFormationType,
                            package_configuration_option: PackageConfigurationOption,
                            drone_type: DroneType) -> DroneFormation:
        return cls.drone_formations_map[package_configuration_option][formation_type][drone_type]

    @classmethod
    def create_default_drone_formations_amounts(cls, drone_type: DroneType) -> {DroneFormation: int}:
        formation_amounts = {}
        for formation_option in PackageConfigurationOption:
            for formation_size in DroneFormationType:
                formation_amounts[cls.drone_formations_map[formation_option][formation_size][drone_type]] = 0
        return formation_amounts


class NoFormationOptionFoundException(Exception):
    pass


class NoDronePackageConfigurationFoundException(Exception):
    pass
