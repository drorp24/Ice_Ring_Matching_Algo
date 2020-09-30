from enum import Enum

from common.entities.drone_model import DroneModel
from common.entities.package import PackageType


class _DroneConfiguration:
    def __init__(self, package_type: PackageType, quantity: int):
        self._package_type = package_type
        self._quantity = quantity

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    @property
    def quantity(self) -> int:
        return self._quantity


class _Drone:
    def __init__(self, drone_model: DroneModel, drone_configuration: [_DroneConfiguration]):
        self._drone_model = drone_model
        self._drone_configuration = drone_configuration

    @property
    def drone_model(self) -> [DroneModel]:
        return self._drone_model

    @property
    def drone_configuration(self) -> [_DroneConfiguration]:
        return self._drone_configuration


class DroneType(Enum):
    DT_1_TINY = _Drone(DroneModel.Model_1, [_DroneConfiguration(PackageType.TINY, 2)])
    DT_1_TINY_MEDIUM = _Drone(DroneModel.Model_1, [_DroneConfiguration(PackageType.TINY, 2),
                                        _DroneConfiguration(PackageType.MEDIUM, 2)])
    DT_2_TINY = _Drone(DroneModel.Model_2, [_DroneConfiguration(PackageType.TINY, 4)])
