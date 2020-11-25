from typing import List

import numpy as np

from common.entities.package import PackageType
from common.math.angle import AngleUnit, Angle
from grid.slide import Slide, SlideProperties
from grid.slides_container import SlidesContainer
from params import MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES
from services.envelope_services_interface import EnvelopeServicesInterface


def create_slide(slide_properties: SlideProperties):
    assert 0 <= slide_properties.cell_required_area <= 1
    return Slide(slide_properties)


def generate_slides_container(service: EnvelopeServicesInterface,
                              package_types: List[PackageType], drone_azimuth_resolution: int,
                              drop_azimuth_resolution: int,
                              cell_width_resolution: float, cell_height_resolution: float,
                              cell_required_area: float) -> SlidesContainer:
    slides = []

    drone_azimuth_options = np.arange(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES,
                                      MAX_AZIMUTH_DEGREES / drone_azimuth_resolution)

    drop_azimuth_options = np.arange(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES,
                                     MAX_AZIMUTH_DEGREES / drop_azimuth_resolution)

    for package_type in package_types:
        for drone_azimuth_option in drone_azimuth_options:
            for drop_azimuth_option in drop_azimuth_options:
                slide_properties = SlideProperties(envelope_service=service,
                                                   package_type=package_type,
                                                   drone_azimuth=Angle(drone_azimuth_option, AngleUnit.DEGREE),
                                                   drop_azimuth=Angle(drop_azimuth_option, AngleUnit.DEGREE),
                                                   cell_width_resolution=cell_width_resolution,
                                                   cell_height_resolution=cell_height_resolution,
                                                   cell_required_area=cell_required_area)
                slide = create_slide(slide_properties)

                slides.append(slide)

    return SlidesContainer(drone_azimuth_resolution, drop_azimuth_resolution, cell_width_resolution,
                           cell_height_resolution, slides=slides)
