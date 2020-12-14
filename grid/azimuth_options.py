import math
from typing import List
from common.math.angle import AngleUnit, Angle
from params import MAX_AZIMUTH_DEGREES, MIN_AZIMUTH_DEGREES


class AzimuthOptions:

    def __init__(self, azimuth_resolution: int):
        self._values = [Angle(value=angle, unit=AngleUnit.DEGREE)
                        for angle in (range(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES,
                                                math.floor(
                                                    (MAX_AZIMUTH_DEGREES - MIN_AZIMUTH_DEGREES)
                                                    / azimuth_resolution)))]

    @property
    def values(self) -> List[Angle]:
        return self._values
