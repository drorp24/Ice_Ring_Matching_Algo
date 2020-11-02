from collections import defaultdict
from typing import List

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from geometry.utils import PolygonUtils
from grid.cell import GridLocation
from grid.slide import Slide
from params import MAX_AZIMUTH_ANGLE


def make_hash() -> defaultdict:
    return defaultdict(make_hash)


class SlidesContainer:

    def __init__(self, drone_azimuth_resolution: int, drop_azimuth_resolution: int,
                 slides: List[Slide]):

        if drone_azimuth_resolution <= 0:
            raise ValueError("Drone azimuth resolution should be more than 0")

        if drop_azimuth_resolution <= 0:
            raise ValueError("Drop azimuth resolution should be more than 0")

        self._drone_azimuth_resolution = drone_azimuth_resolution
        self._drone_azimuth_delta_deg = Angle(MAX_AZIMUTH_ANGLE / self._drone_azimuth_resolution,
                                              AngleUnit.DEGREE)

        if not self._drone_azimuth_delta_deg.in_degrees().is_integer():
            raise ValueError(MAX_AZIMUTH_ANGLE, "should be divided by drone azimuth resolution with no remainder")

        self._drop_azimuth_resolution = drop_azimuth_resolution
        self._drop_azimuth_delta_deg = Angle(MAX_AZIMUTH_ANGLE / self._drop_azimuth_resolution,
                                             AngleUnit.DEGREE)

        if not self._drop_azimuth_delta_deg.in_degrees().is_integer():
            raise ValueError(MAX_AZIMUTH_ANGLE, "should be divided by drop azimuth resolution with no remainder")

        self._hash = make_hash()
        for slide in slides:
            self._hash[slide.package_type][slide.drone_azimuth.in_degrees()][
                slide.drop_azimuth.in_degrees()] = slide

    @property
    def hash(self) -> defaultdict:
        return self._hash

    @property
    def get_drone_azimuth_resolution(self) -> int:
        return self._drone_azimuth_resolution

    @property
    def get_drop_azimuth_resolution(self) -> int:
        return self._drop_azimuth_resolution

    def get_envelope_locations(self, drone_azimuth: Angle, drop_azimuth: Angle,
                               package_type: PackageType) -> List[GridLocation]:

        round_drone_azimuth = PolygonUtils.convert_nearest_value_in_resolution(
                drone_azimuth.in_degrees(),
                int(self._drone_azimuth_delta_deg.in_degrees()))

        round_drop_azimuth = PolygonUtils.convert_nearest_value_in_resolution(
                drop_azimuth.in_degrees(),
                int(self._drop_azimuth_delta_deg.in_degrees()))

        return self._hash[package_type][round_drone_azimuth][round_drop_azimuth].envelope_locations
