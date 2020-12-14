import math


def convert_ratio_to_required_area(box_resolution: int, box_ratio_required: float):
    return box_resolution ** 2 * box_ratio_required


def convert_higher_value_in_resolution(value: float, resolution: int) -> int:
    return math.ceil(value / resolution) * resolution


def convert_lower_value_in_resolution(value: float, resolution: int) -> int:
    return math.floor(value / resolution) * resolution


def convert_nearest_value_in_resolution(value: float, resolution: int) -> int:
    return round(value / resolution) * resolution
