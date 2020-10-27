from typing import List

import numpy as np

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from grid.slide import Slide
from grid.slides_container import SlidesContainer
from params import MAX_AZIMUTH_ANGLE, MIN_AZIMUTH_ANGLE
from services.envelope_services_interface import EnvelopeServicesInterface


def generate_slides_container(service: EnvelopeServicesInterface,
                              package_types: List[PackageType], drone_azimuth_resolution: int,
                              drop_azimuth_resolution: int,
                              cell_resolution: int, cell_ratio_required: float) -> SlidesContainer:
    slides = []

    drone_azimuth_delta_deg = Angle(MAX_AZIMUTH_ANGLE / drone_azimuth_resolution, AngleUnit.DEGREE)
    drone_azimuth_steps = np.arrange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE, drone_azimuth_delta_deg)

    drop_azimuth_deg = Angle(MAX_AZIMUTH_ANGLE / drop_azimuth_resolution, AngleUnit.DEGREE)
    drop_azimuth_steps = np.arrange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE, drop_azimuth_deg)

    for package_type in package_types:
        for drone_azimuth_step in drone_azimuth_steps:
            for drop_azimuth_step in drop_azimuth_steps:
                slides.append(Slide(service,
                                    package_type, drone_azimuth_step, drop_azimuth_step,
                                    cell_resolution, cell_ratio_required))

    return SlidesContainer(drone_azimuth_resolution, drop_azimuth_resolution, slides=slides)
