import math

import numpy as np
from optional import Optional

from common.math.angle import Angle, AngleUnit
from grid.cell import EnvelopeCell
from params import MAX_PITCH_DEGREES


class CellServices:
    ANGLE_DELTA_COST = 10

    @staticmethod
    def get_distance(cell1: EnvelopeCell, cell2: EnvelopeCell) -> float:
        if cell1.location.is_empty() \
                or cell2.location.is_empty():
            return np.inf

        angle_delta = cell1.drone_azimuth.calc_abs_difference(cell2.drone_azimuth)
        location_delta = cell1.location.get() - cell2.location.get()
        dist = np.linalg.norm([location_delta.row, location_delta.column])
        angle_delta_cost = (math.cos(angle_delta.radians) - 1) / -2
        return dist + CellServices.ANGLE_DELTA_COST / (dist + 1) * angle_delta_cost

    @staticmethod
    def get_drop_azimuth(drone_azimuth: Angle, drop_azimuth: Angle, drop_pitch: Angle) -> Angle:
        return drone_azimuth if drop_pitch == Angle(MAX_PITCH_DEGREES, AngleUnit.DEGREE) else drop_azimuth
