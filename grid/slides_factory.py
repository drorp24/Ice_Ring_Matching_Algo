from typing import List

import numpy as np

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from grid.slide import Slide
from grid.slides_container import SlidesContainer
from params import MAX_AZIMUTH_ANGLE, MIN_AZIMUTH_ANGLE


def generate_slides_container(package_types: List[PackageType], drone_azimuth_resolution: int,
                              package_delivery_plan_azimuth_resolution: int) -> SlidesContainer:
    slides = []

    drone_azimuth_delta_deg = Angle(MAX_AZIMUTH_ANGLE / drone_azimuth_resolution, AngleUnit.DEGREE)
    drone_azimuth_steps = np.arrange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE, drone_azimuth_delta_deg)

    package_delivery_plan_azimuth_deg = Angle(MAX_AZIMUTH_ANGLE / package_delivery_plan_azimuth_resolution, AngleUnit.DEGREE)
    package_delivery_plan_azimuth_steps = np.arrange(MIN_AZIMUTH_ANGLE, MAX_AZIMUTH_ANGLE, package_delivery_plan_azimuth_deg)

    for package_type in package_types:
        for drone_azimuth_step in drone_azimuth_steps:
            for package_delivery_plan_azimuth_step in package_delivery_plan_azimuth_steps:
                slides.append(Slide(package_type, drone_azimuth_step, package_delivery_plan_azimuth_step))

    SlidesContainer(drone_azimuth_resolution, package_delivery_plan_azimuth_resolution, slides=slides )
