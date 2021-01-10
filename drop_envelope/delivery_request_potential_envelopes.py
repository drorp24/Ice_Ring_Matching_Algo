from typing import List

from common.entities.base_entities.delivery_request import DeliveryRequest
from drop_envelope.abstract_envelope_collections import PotentialEnvelopeCollection, ShapeableCollection
from drop_envelope.potential_drop_envelope import PotentialDropEnvelopes
from geometry.geo2d import Point2D


class DeliveryRequestPotentialEnvelopes(PotentialEnvelopeCollection):

    def __init__(self, potential_drop_envelopes: List[PotentialDropEnvelopes], delivery_request: DeliveryRequest):
        self._potential_envelopes = potential_drop_envelopes
        self._centroid = delivery_request.calc_location()

    @property
    def potential_envelopes(self) -> List[PotentialDropEnvelopes]:
        return self._potential_envelopes

    @property
    def centroid(self) -> Point2D:
        return self.centroid

    def get_potential_envelopes(self) -> List[ShapeableCollection]:
        return self._potential_envelopes

    def get_centroid(self) -> Point2D:
        return self.centroid
