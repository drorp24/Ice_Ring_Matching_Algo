import math

import numpy as np

from common.math.angle import Angle, AngleUnit
from common.utils import distance_calculator
from grid.grid_cell import EnvelopeGridCell
from params import MAX_PITCH_DEGREES


class GridCellServices:

    @staticmethod
    def calc_distance(cell1: EnvelopeGridCell, cell2: EnvelopeGridCell) -> float:
        if cell1.location.is_empty() \
                or cell2.location.is_empty():
            return np.inf

        return distance_calculator.calc_distance(cell1.location.get(), cell1.drone_azimuth,
                                                 cell2.location.get(), cell2.drone_azimuth)

    @staticmethod
    def get_drop_azimuth(drone_azimuth: Angle, drop_azimuth: Angle, drop_pitch: Angle) -> Angle:
        return drone_azimuth if drop_pitch == Angle(MAX_PITCH_DEGREES, AngleUnit.DEGREE) else drop_azimuth
