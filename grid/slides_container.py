from collections import defaultdict
from typing import List

from flatten_dict import flatten
from flatten_dict.reducer import underscore_reducer
from optional import Optional

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from grid.grid_geometry_utils import convert_nearest_value_in_resolution
from grid.grid_location import GridLocation
from grid.slide import Slide
from params import MAX_AZIMUTH_DEGREES, MIN_AZIMUTH_DEGREES


def make_dict() -> defaultdict:
    return defaultdict(make_dict)


class SlidesContainer:

    def __init__(self, drone_azimuth_resolution: int, drop_azimuth_resolution: int,
                 cell_width_resolution: float, cell_height_resolution: float, slides: List[Slide]):

        self.is_drone_az_resolution_positive(drone_azimuth_resolution)
        self.is_drop_az_resolution_positive(drop_azimuth_resolution)

        self._drone_azimuth_resolution = drone_azimuth_resolution
        self._drone_azimuth_delta_deg = Angle((MAX_AZIMUTH_DEGREES - MIN_AZIMUTH_DEGREES) / self._drone_azimuth_resolution,
                                              AngleUnit.DEGREE)
        self.is_drone_azimuth_delta_deg_integer()

        self._drop_azimuth_resolution = drop_azimuth_resolution
        self._drop_azimuth_delta_deg = Angle((MAX_AZIMUTH_DEGREES - MIN_AZIMUTH_DEGREES) / self._drop_azimuth_resolution,
                                             AngleUnit.DEGREE)
        self.is_drop_azimuth_delta_deg_integer()

        self._cell_width_resolution = cell_width_resolution
        self._cell_height_resolution = cell_height_resolution

        self._slides_container = make_dict()
        for slide in slides:
            self._slides_container[slide.package_type][slide.drone_azimuth.degrees][
                slide.drop_azimuth.degrees] = slide

    def is_drop_azimuth_delta_deg_integer(self):
        if not self._drop_azimuth_delta_deg.degrees.is_integer():
            raise ValueError(MAX_AZIMUTH_DEGREES, "should be divided by drop azimuth resolution with no remainder")

    def is_drone_azimuth_delta_deg_integer(self):
        if not self._drone_azimuth_delta_deg.degrees.is_integer():
            raise ValueError(MAX_AZIMUTH_DEGREES, "should be divided by drone azimuth resolution with no remainder")

    def is_drop_az_resolution_positive(self, drop_azimuth_resolution):
        if drop_azimuth_resolution <= 0:
            raise ValueError("Drop azimuth resolution should be more than 0")

    def is_drone_az_resolution_positive(self, drone_azimuth_resolution):
        if drone_azimuth_resolution <= 0:
            raise ValueError("Drone azimuth resolution should be more than 0")

    @property
    def hash(self) -> defaultdict:
        return self._slides_container

    @property
    def get_drone_azimuth_resolution(self) -> int:
        return self._drone_azimuth_resolution

    @property
    def get_drop_azimuth_resolution(self) -> int:
        return self._drop_azimuth_resolution

    @property
    def cell_width_resolution(self) -> float:
        return self._cell_width_resolution

    @property
    def cell_height_resolution(self) -> float:
        return self._cell_height_resolution

    def get_envelope_location(self, drone_azimuth: Angle, drop_azimuth: Angle,
                              package_type: PackageType) -> Optional.of(GridLocation):

        round_drone_azimuth = Angle(convert_nearest_value_in_resolution(
            drone_azimuth.degrees,
            int(self._drone_azimuth_delta_deg.degrees)), AngleUnit.DEGREE)

        round_drop_azimuth = Angle(convert_nearest_value_in_resolution(
            drop_azimuth.degrees,
            int(self._drop_azimuth_delta_deg.degrees)), AngleUnit.DEGREE)

        return self._slides_container[package_type][round_drone_azimuth.degrees][round_drop_azimuth.degrees].envelope_location

    def flatten_hash(self):
        return flatten(self._slides_container, reducer=underscore_reducer)
