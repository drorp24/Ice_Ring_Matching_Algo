from typing import Union
from optional import Optional

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from drop_envelope.azimuth_quantization import get_azimuth_quantization_values
from drop_envelope.drop_envelope import DropEnvelope, DropEnvelopeProperties
from drop_envelope.potential_drop_envelope import PotentialDropEnvelopes
from drop_envelope.slide_service import MockSlidesServiceWrapper
from geometry.geo2d import Point2D


def get_drop_envelope(drone_azimuth: Angle, drop_azimuth: Optional.of(Angle), package_type: PackageType,
                      drop_point: Point2D) -> DropEnvelope:
    drop_envelope_properties = DropEnvelopeProperties(drop_point=drop_point,
                                                      drop_azimuth=drop_azimuth,
                                                      drone_azimuth=drone_azimuth,
                                                      package_type=package_type)
    return DropEnvelope(drop_envelope_properties)


def get_potential_drop_envelope(drop_azimuth: Optional.of(Angle), package_type: PackageType,
                                drop_point: Point2D) -> PotentialDropEnvelopes:
    drone_azimuths = get_azimuth_quantization_values(MockSlidesServiceWrapper.drone_azimuth_level_amount)
    drop_envelopes = list(map(lambda x: DropEnvelope(DropEnvelopeProperties(
        package_type=package_type,
        drop_azimuth=drop_azimuth,
        drop_point=drop_point,
        drone_azimuth=x)), drone_azimuths))
    return PotentialDropEnvelopes(drop_envelopes)
