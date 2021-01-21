from typing import List

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from drop_envelope.slide import Slide


class SlideContainer:
    def __init__(self):
        self._slides_dict = {}

    @property
    def slides(self) -> dict:
        return self._slides_dict

    def add_slide(self, slide: Slide):
        self._slides_dict[(int(slide.drop_azimuth.degrees), int(slide.drone_azimuth.degrees), slide.package_type)] \
            = slide

    def add_slides(self, slides: List[Slide]):
        for slide in slides:
            self._slides_dict[(int(slide.drop_azimuth.degrees), int(slide.drone_azimuth.degrees), slide.package_type)]\
                = slide

    def get_slide(self, drop_azimuth: Angle, drone_azimuth: Angle, package_type: PackageType) -> Slide:
        return self._slides_dict[(int(drop_azimuth.degrees), int(drone_azimuth.degrees), package_type)]
