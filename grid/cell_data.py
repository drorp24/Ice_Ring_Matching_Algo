from abc import ABC

from attr import dataclass

from common.math.angle import Angle


class CellData(ABC):
    def __init__(self):
        super().__init__()


@dataclass
class EnvelopeCellData(CellData):
    drone_azimuth: Angle
