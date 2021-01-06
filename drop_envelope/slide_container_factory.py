from common.entities.base_entities.package import PackageType
from drop_envelope.slide import Slide, SlideProperties
from drop_envelope.slide_container import SlideContainer
from drop_envelope.azimuth_quantization import get_azimuth_quantization_values
from services.envelope_services_interface import EnvelopeServicesInterface
from services.mock_envelope_services import MockEnvelopeServices


def create_slides_container(drop_azimuth_level_amounts: int, drone_azimuth_level_amounts: int,
                            envelope_service: EnvelopeServicesInterface = MockEnvelopeServices()) -> SlideContainer:
    slide_container = SlideContainer()
    drone_azimuth_values = get_azimuth_quantization_values(drone_azimuth_level_amounts)
    drop_azimuth_values = list(set(get_azimuth_quantization_values(drop_azimuth_level_amounts)) |
                               set(drone_azimuth_values))

    for package_type in PackageType:
        for drop_azimuth in drop_azimuth_values:
            for drone_azimuth in drone_azimuth_values:
                slide_container.add_slide(Slide(SlideProperties(package_type=package_type,
                                                                drone_azimuth=drone_azimuth,
                                                                drop_azimuth=drop_azimuth),
                                                envelope_service=envelope_service))
    return slide_container
