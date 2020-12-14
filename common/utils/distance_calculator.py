from common.math.angle import Angle
import numpy as np

from grid.grid_location import GridLocation

ANGLE_DELTA_COST = 10

def calc_distance(start_point:GridLocation, start_angle:Angle, end_point:GridLocation, end_angle:Angle) -> float:
    angle_delta = start_angle.calc_abs_difference(end_angle)
    location_delta = start_point - end_point
    dist = np.linalg.norm([location_delta.row, location_delta.column])
    angle_delta_cost = (np.math.cos(angle_delta.radians) - 1) / -2
    return dist + ANGLE_DELTA_COST / (dist + 1) * angle_delta_cost