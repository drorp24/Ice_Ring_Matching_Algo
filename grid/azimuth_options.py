import math
from typing import List

import numpy as np

from common.math.angle import AngleUnit, Angle


class AzimuthOptions:

    def __init__(self, azimuth_resolution: int):
        self._values = [Angle(value=angle, unit=AngleUnit.DEGREE)
                        for angle in (np.arange(0, AngleUnit.DEGREE.value,
                                                math.floor(
                                                    AngleUnit.DEGREE.value
                                                    / azimuth_resolution)))]

    @property
    def values(self) -> List[Angle]:
        return self._values
