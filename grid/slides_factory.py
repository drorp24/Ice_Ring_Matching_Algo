from typing import List

import numpy as np

from common.entities.package import PackageType
from common.math.angle import AngleUnit, Angle
from grid.slide import Slide
from grid.slides_container import SlidesContainer
from params import MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES
from services.envelope_services_interface import EnvelopeServicesInterface


def create_slide(service: EnvelopeServicesInterface,
                 package_type: PackageType, drone_azimuth: Angle, drop_azimuth: Angle,
                 cell_resolution: int, cell_ratio_required: float):
    assert 0 <= cell_ratio_required <= 1
    return Slide(service,
                 package_type, drone_azimuth, drop_azimuth,
                 cell_resolution, cell_ratio_required)


def generate_slides_container(service: EnvelopeServicesInterface,
                              package_types: List[PackageType], drone_azimuth_resolution: int,
                              drop_azimuth_resolution: int,
                              cell_resolution: int, cell_ratio_required: float) -> SlidesContainer:
    slides = []

    drone_azimuth_options = np.arange(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES,
                                      MAX_AZIMUTH_DEGREES / drone_azimuth_resolution)

    drop_azimuth_options = np.arange(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES,
                                     MAX_AZIMUTH_DEGREES / drop_azimuth_resolution)

    for package_type in package_types:
        for drone_azimuth_option in drone_azimuth_options:
            for drop_azimuth_option in drop_azimuth_options:
                slide = create_slide(service,
                                     package_type, Angle(drone_azimuth_option, AngleUnit.DEGREE),
                                     Angle(drop_azimuth_option, AngleUnit.DEGREE),
                                     cell_resolution, cell_ratio_required)

                slides.append(slide)

    return SlidesContainer(drone_azimuth_resolution, drop_azimuth_resolution, slides=slides)
