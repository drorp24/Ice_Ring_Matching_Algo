from enum import Enum, IntEnum
from common.entities.package import PackageType


class _PlatformType(IntEnum):
    PLATFORM_1 = 4
    PLATFORM_2 = 6


class _PackageTypesVolumeMap:

    def __init__(self, packages_types_volume: [int]):
        keys = [package_type for package_type in PackageType]
        for key, volume in enumerate(keys, packages_types_volume):
            self._dict[key] = packages_types_volume[volume]

    @property
    def dict(self) -> dict:
        return self._dict

    def get_package_types(self) -> [PackageType]:
        return self._dict.keys()

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self._dict[package_type]

    def get_package_types_volumes(self) -> [int]:
        return self._dict.values()


class _DroneConfiguration:

    def __init__(self, platform_type: _PlatformType, package_types_map: _PackageTypesVolumeMap):
        self._platform_type = platform_type
        self._package_types_map = package_types_map

    @property
    def platform_type(self) -> _PlatformType:
        return self._platform_type

    @property
    def package_type_map(self) -> _PackageTypesVolumeMap:
        return self._package_types_map

    def get_package_type_volume(self, package_type: PackageType) -> int:
        return self._package_types_map.get_package_type_volume(package_type)


class DroneConfigurationType(Enum):
    PLATFORM_1_2X8 = _DroneConfiguration(_PlatformType.PLATFORM_1, _PackageTypesVolumeMap([0, 0, 0, 2]))
    PLATFORM_1_4X4 = _DroneConfiguration(_PlatformType.PLATFORM_1, _PackageTypesVolumeMap([0, 0, 4, 0]))
    PLATFORM_1_8X2 = _DroneConfiguration(_PlatformType.PLATFORM_1, _PackageTypesVolumeMap([0, 8, 0, 0]))
    PLATFORM_1_16X1 = _DroneConfiguration(_PlatformType.PLATFORM_1, _PackageTypesVolumeMap([16, 0, 0, 0]))
    PLATFORM_2_4X8 = _DroneConfiguration(_PlatformType.PLATFORM_2, _PackageTypesVolumeMap([0, 0, 0, 4]))
    PLATFORM_2_8X4 = _DroneConfiguration(_PlatformType.PLATFORM_2, _PackageTypesVolumeMap([0, 0, 8, 0]))
    PLATFORM_2_16X2 = _DroneConfiguration(_PlatformType.PLATFORM_2, _PackageTypesVolumeMap([0, 16, 0, 0]))
    PLATFORM_2_32X1 = _DroneConfiguration(_PlatformType.PLATFORM_2, _PackageTypesVolumeMap([32, 0, 0, 0]))