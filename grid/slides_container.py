from collections import defaultdict
from typing import List

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from grid.cell import Location
from grid.slide import Slide
from params import MAX_AZIMUTH_ANGLE


def make_hash() -> defaultdict:
    return defaultdict(make_hash)


class SlidesContainer:

    def __init__(self, drone_azimuth_resolution: int, package_delivery_plan_azimuth_resolution: int,
                 slides: List[Slide]):

        if drone_azimuth_resolution <= 0:
            raise ValueError("Drone azimuth resolution should be more than 0")

        if package_delivery_plan_azimuth_resolution <= 0:
            raise ValueError("Package Delivery Plan azimuth resolution should be more than 0")

        self._drone_azimuth_resolution = drone_azimuth_resolution
        self._drone_azimuth_delta_deg = Angle(MAX_AZIMUTH_ANGLE / self._drone_azimuth_resolution,
                                          AngleUnit.DEGREE)

        self._package_delivery_plan_azimuth_resolution = package_delivery_plan_azimuth_resolution
        self._package_delivery_plan_azimuth_delta_deg = Angle(MAX_AZIMUTH_ANGLE / self._package_delivery_plan_azimuth_resolution,
                                                          AngleUnit.DEGREE)

        self._hash = make_hash()
        for slide in slides:
            self._hash[slide.package_type][slide.drone_azimuth][
                slide.package_delivery_plan_azimuth] = slide

    @property
    def hash(self) -> defaultdict:
        return self._hash

    @property
    def get_drone_azimuth_resolution(self) -> int:
        return self._drone_azimuth_resolution

    @property
    def get_package_delivery_plan_azimuth_resolution(self) -> int:
        return self._package_delivery_plan_azimuth_resolution

    def get_envelope_locations(self, drone_azimuth: Angle, package_delivery_plan_azimuth: Angle,
                               package_type: PackageType) -> List[Location]:
        round_drone_azimuth = round(
            drone_azimuth.in_degrees() / self._drone_azimuth_delta_deg.in_degrees()) * \
                              self._drone_azimuth_delta_deg.in_degrees()

        round_package_delivery_plan_azimuth = round(
            package_delivery_plan_azimuth.in_degrees() / self._package_delivery_plan_azimuth_delta_deg.in_degrees()) * \
                                              self._package_delivery_plan_azimuth_delta_deg.in_degrees()

        return self._hash[package_type][round_drone_azimuth][round_package_delivery_plan_azimuth].envelope_locations
