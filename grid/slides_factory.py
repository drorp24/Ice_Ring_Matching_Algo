import itertools
from typing import List

import numpy as np

from common.entities.package import PackageType
from common.math.angle import AngleUnit, Angle
from grid.slide import Slide, SlideProperties
from grid.slides_container import SlidesContainer
from params import MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES
from services.envelope_services_interface import EnvelopeServicesInterface


def create_slide(slide_properties: SlideProperties):
    assert 0 <= slide_properties.minimal_area <= 1
    return Slide(slide_properties)


def generate_slides_container(service: EnvelopeServicesInterface,
                              package_types: List[PackageType], drone_azimuth_resolution: int,
                              drop_azimuth_resolution: int,
                              cell_width_resolution: float, cell_height_resolution: float,
                              minimal_area: float) -> SlidesContainer:
    slides = []

    drone_azimuth_options = np.arange(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES,
                                      (MAX_AZIMUTH_DEGREES - MIN_AZIMUTH_DEGREES) / drone_azimuth_resolution)

    drop_azimuth_options = np.arange(MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES,
                                     (MAX_AZIMUTH_DEGREES - MIN_AZIMUTH_DEGREES) / drop_azimuth_resolution)


    for package_type, drone_azimuth_option, drop_azimuth_option in itertools.product(package_types,drone_azimuth_options,drop_azimuth_options):
        slide_properties = SlideProperties(envelope_service=service,
                                           package_type=package_type,
                                           drone_azimuth=Angle(drone_azimuth_option, AngleUnit.DEGREE),
                                           drop_azimuth=Angle(drop_azimuth_option, AngleUnit.DEGREE),
                                           cell_width_resolution=cell_width_resolution,
                                           cell_height_resolution=cell_height_resolution,
                                           minimal_area=minimal_area)
        slide = create_slide(slide_properties)

        slides.append(slide)

    return SlidesContainer(drone_azimuth_resolution, drop_azimuth_resolution, cell_width_resolution,
                           cell_height_resolution, slides=slides)
