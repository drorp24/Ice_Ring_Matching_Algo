from typing import List

import numpy as np

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from grid.slide import Slide
from grid.slides_container import SlidesContainer
from params import MAX_AZIMUTH_ANGLE, MIN_AZIMUTH_ANGLE
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

    drone_azimuth_delta_deg = Angle(MAX_AZIMUTH_ANGLE / drone_azimuth_resolution, AngleUnit.DEGREE)
    drone_azimuth_steps = np.arange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE, drone_azimuth_delta_deg.in_degrees())

    drop_azimuth_deg = Angle(MAX_AZIMUTH_ANGLE / drop_azimuth_resolution, AngleUnit.DEGREE)
    drop_azimuth_steps = np.arange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE, drop_azimuth_deg.in_degrees())

    for package_type in package_types:
        for drone_azimuth_step in drone_azimuth_steps:
            for drop_azimuth_step in drop_azimuth_steps:
                slide = create_slide(service,
                                     package_type, drone_azimuth_step, drop_azimuth_step,
                                     cell_resolution, cell_ratio_required)

                slides.append(slide)

    return SlidesContainer(drone_azimuth_resolution, drop_azimuth_resolution, slides=slides)
