from optional import Optional
from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from drop_envelope.azimuth_quantization import get_azimuth_quantization_value
from drop_envelope.slide import Slide
from drop_envelope.slide_container_factory import create_slides_container


class _SlidesService:
    def __init__(self, drop_azimuth_level_amounts: int, drone_azimuth_level_amounts: int):
        self.drop_azimuth_level_amount = drop_azimuth_level_amounts
        self.drone_azimuth_level_amount = drone_azimuth_level_amounts
        self.slide_container = create_slides_container(drop_azimuth_level_amounts, drone_azimuth_level_amounts)

    def get_slide(self, drone_azimuth: Angle, drop_azimuth: Optional.of(Angle), package_type: PackageType) -> Slide:
        drone_quantization_azimuth = get_azimuth_quantization_value(drone_azimuth, self.drone_azimuth_level_amount)
        if drop_azimuth is None:
            drop_quantization_azimuth = drone_quantization_azimuth
        else:
            drop_quantization_azimuth = get_azimuth_quantization_value(drop_azimuth, self.drop_azimuth_level_amount)
        return self.slide_container.get_slide(drop_quantization_azimuth, drone_quantization_azimuth, package_type)


class MockSlidesServiceWrapper:
    drop_azimuth_level_amount = 8
    drone_azimuth_level_amount = 8
    service = _SlidesService(drop_azimuth_level_amount, drone_azimuth_level_amount)

    @staticmethod
    def get_slide(drone_azimuth: Angle, drop_azimuth: Angle, package_type: PackageType) -> Slide:
        return MockSlidesServiceWrapper.service.get_slide(drone_azimuth, drop_azimuth, package_type)
