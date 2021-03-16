import math
from typing import List

from optional import Optional
from optional.nothing import Nothing

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from drop_envelope.azimuth_quantization import get_azimuth_quantization_value, get_azimuth_quantization_values
from drop_envelope.slide import Slide
from drop_envelope.slide_container_factory import create_slides_container
from params import MIN_AZIMUTH_DEGREES, MAX_AZIMUTH_DEGREES


class _SlidesService:
    def __init__(self, drop_azimuth_level_amounts: int, drone_azimuth_level_amounts: int):
        self.drop_azimuth_level_amount = drop_azimuth_level_amounts
        self.drone_azimuth_level_amount = drone_azimuth_level_amounts
        self.slide_container = create_slides_container(drop_azimuth_level_amounts, drone_azimuth_level_amounts)

    def get_slide(self, drone_azimuth: Angle, drop_azimuth: Angle, package_type: PackageType) -> Slide:
        drone_quantization_azimuth = get_azimuth_quantization_value(drone_azimuth, self.drone_azimuth_level_amount)
        drop_quantization_azimuth = get_azimuth_quantization_value(drop_azimuth, self.drop_azimuth_level_amount)
        return self.slide_container.get_slide(drop_quantization_azimuth, drone_quantization_azimuth, package_type)


class MockSlidesServiceWrapper:
    drop_azimuth_level_amount = 8
    drone_azimuth_level_amount = 8
    service = _SlidesService(drop_azimuth_level_amount, drone_azimuth_level_amount)

    @staticmethod
    def get_slide(drone_azimuth: Angle, drop_azimuth: Angle, package_type: PackageType) -> Slide:
        return MockSlidesServiceWrapper.service.get_slide(drone_azimuth, drop_azimuth, package_type)

    @classmethod
    def get_drone_azimuth_level_values(cls) -> List[Angle]:
        return get_azimuth_quantization_values(cls.drone_azimuth_level_amount)

    @classmethod
    def get_drop_azimuth_level_values(cls) -> List[Angle]:
        return get_azimuth_quantization_values(cls.drop_azimuth_level_amount)
