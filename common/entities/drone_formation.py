from common.entities.drone import DroneConfigurationType
from enum import IntEnum, Enum


class FormationSize(IntEnum):
    MINI = 2
    MEDIUM = 4


class _DroneFormation:

    def __init__(self, formation_size: FormationSize, drone_configuration: DroneConfigurationType):
        self._size = formation_size
        self._drone_configuration = drone_configuration

    @property
    def size(self) -> FormationSize:
        return self._size

    @property
    def drone_configuration(self) -> DroneConfigurationType:
        return self._drone_configuration


class DroneFormationType(Enum):
    _2X_PLATFORM_1_2X8 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_1_2X8)
    _4X_PLATFORM_1_2X8 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_1_2X8)
    _2X_PLATFORM_1_4X4 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_1_4X4)
    _4X_PLATFORM_1_4X4 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_1_4X4)
    _2X_PLATFORM_1_8X2 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_1_8X2)
    _4X_PLATFORM_1_8X2 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_1_8X2)
    _2X_PLATFORM_1_16X1 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_1_16X1)
    _4X_PLATFORM_1_16X1 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_1_16X1)
    _2X_PLATFORM_2_4X8 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_2_4X8)
    _4X_PLATFORM_2_4X8 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_2_4X8)
    _2X_PLATFORM_2_8X4 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_2_8X4)
    _4X_PLATFORM_2_8X4 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_2_8X4)
    _2X_PLATFORM_2_16X2 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_2_16X2)
    _4X_PLATFORM_2_16X2 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_2_16X2)
    _2X_PLATFORM_2_32X1 = _DroneFormation(FormationSize.MINI, DroneConfigurationType.PLATFORM_2_32X1)
    _4X_PLATFORM_2_32X1 = _DroneFormation(FormationSize.MEDIUM, DroneConfigurationType.PLATFORM_2_32X1)
