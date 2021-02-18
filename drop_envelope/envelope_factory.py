from optional import Optional

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from drop_envelope.azimuth_quantization import get_azimuth_quantization_values
from drop_envelope.delivery_request_envelope import DeliveryRequestPotentialEnvelope
from drop_envelope.drop_envelope import DropEnvelope, DropEnvelopeProperties
from drop_envelope.loading_dock_envelope import LoadingDockPotentialEnvelope
from drop_envelope.potential_drop_envelope import PotentialDropEnvelopes
from drop_envelope.slide_service import MockSlidesServiceWrapper
from geometry.geo2d import Point2D, Polygon2D, EmptyGeometry2D


def create_drop_envelope(drone_azimuth: Angle, drop_azimuth: Optional.of(Angle), package_type: PackageType,
                         drop_point: Point2D) -> DropEnvelope:
    if drop_azimuth.is_empty():
        drop_azimuth = Optional.of(drone_azimuth)
    drop_envelope_properties = DropEnvelopeProperties(drop_point=drop_point,
                                                      drop_azimuth=drop_azimuth.get(),
                                                      drone_azimuth=drone_azimuth,
                                                      package_type=package_type)
    return DropEnvelope(drop_envelope_properties)


def create_potential_drop_envelope(drop_azimuth: Optional.of(Angle), package_type: PackageType,
                                   drop_point: Point2D) -> PotentialDropEnvelopes:
    drone_azimuths = get_azimuth_quantization_values(MockSlidesServiceWrapper.drone_azimuth_level_amount)
    if drop_azimuth.is_empty():
        drop_envelopes = list(map(lambda drone_azimuth: DropEnvelope(DropEnvelopeProperties(
            package_type=package_type,
            drop_azimuth=drone_azimuth,
            drop_point=drop_point,
            drone_azimuth=drone_azimuth)), drone_azimuths))
    else:
        drop_envelopes = list(map(lambda drone_azimuth: DropEnvelope(DropEnvelopeProperties(
            package_type=package_type,
            drop_azimuth=drop_azimuth.get(),
            drop_point=drop_point,
            drone_azimuth=drone_azimuth)), drone_azimuths))
    drop_envelopes = list(filter(lambda drop_envelope: isinstance(drop_envelope.internal_envelope, Polygon2D),
                                 drop_envelopes))
    return PotentialDropEnvelopes(drop_point=drop_point,
                                  drop_azimuth=drop_azimuth,
                                  drop_envelopes=drop_envelopes)


def create_delivery_request_envelope(delivery_request: DeliveryRequest, chosen_delivery_option_index: int = 0) \
        -> DeliveryRequestPotentialEnvelope:
    package_delivery_plans = delivery_request.delivery_options[chosen_delivery_option_index].package_delivery_plans
    dr_potential_drop_envelopes = list(map(
        lambda pdp: create_potential_drop_envelope(drop_azimuth=Optional.of(pdp.azimuth),
                                                   package_type=pdp.package_type,
                                                   drop_point=pdp.drop_point), package_delivery_plans))
    return DeliveryRequestPotentialEnvelope(potential_drop_envelopes=dr_potential_drop_envelopes,
                                            centroid=delivery_request.calc_location())


def create_loading_dock_envelope(drone_loading_dock: DroneLoadingDock) -> LoadingDockPotentialEnvelope:
    return LoadingDockPotentialEnvelope(drone_loading_dock=drone_loading_dock)