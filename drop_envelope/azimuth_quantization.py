import math
from typing import List

from common.math.angle import AngleUnit, Angle
from params import MAX_AZIMUTH_DEGREES, MIN_AZIMUTH_DEGREES


def get_azimuth_quantization_value(azimuth: Angle, levels: int = 8) -> Angle:
    assert MAX_AZIMUTH_DEGREES > azimuth.degrees >= MIN_AZIMUTH_DEGREES
    resolution = (MAX_AZIMUTH_DEGREES - MIN_AZIMUTH_DEGREES) / levels
    return Angle(MIN_AZIMUTH_DEGREES + math.floor(azimuth.degrees / resolution) * resolution, unit=AngleUnit.DEGREE)


def get_azimuth_quantization_values(levels: int = 8) -> List[Angle]:
    return list(map(lambda x: Angle(x, unit=AngleUnit.DEGREE), range(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES, levels)))
