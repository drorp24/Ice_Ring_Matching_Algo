from typing import List

from optional import Optional

from common.entities.base_entities.delivery_request import DeliveryRequest
from drop_envelope.envelope_collections import PotentialEnvelopeCollection, ShapeableCollection
from drop_envelope.potential_drop_envelope import PotentialDropEnvelopes
from geometry.geo2d import Point2D


class DeliveryRequestPotentialEnvelope(PotentialEnvelopeCollection):

    def __init__(self, potential_drop_envelopes: List[PotentialDropEnvelopes], centroid: Point2D):
        self._potential_drop_envelopes = potential_drop_envelopes
        self._centroid = centroid

    @classmethod
    def from_delivery_request(cls, delivery_request: DeliveryRequest, chosen_delivery_option_index: int = 0):
        package_delivery_plans = delivery_request.delivery_options[chosen_delivery_option_index].package_delivery_plans
        dr_potential_drop_envelopes = [
            PotentialDropEnvelopes.from_drop_envelope_properties(drop_azimuth=Optional.of(pdp.azimuth),
                                                                 package_type=pdp.package_type,
                                                                 drop_point=pdp.drop_point) for pdp in
            package_delivery_plans]
        return DeliveryRequestPotentialEnvelope(potential_drop_envelopes=dr_potential_drop_envelopes,
                                                centroid=delivery_request.calc_location())

    @property
    def centroid(self) -> Point2D:
        return self._centroid

    def get_centroid(self) -> Point2D:
        return self.centroid

    @property
    def potential_drop_envelopes(self) -> List[PotentialDropEnvelopes]:
        return self._potential_drop_envelopes

    def get_shapeable_collection(self) -> List[ShapeableCollection]:
        return self.potential_drop_envelopes
