from typing import List

from drop_envelope.envelope_collections import PotentialEnvelopeCollection, ShapeableCollection
from drop_envelope.potential_drop_envelope import PotentialDropEnvelopes
from geometry.geo2d import Point2D


class DeliveryRequestPotentialEnvelope(PotentialEnvelopeCollection):
    def __init__(self, potential_drop_envelopes: List[PotentialDropEnvelopes], centroid: Point2D):
        self._potential_drop_envelopes = potential_drop_envelopes
        self._centroid = centroid

    @property
    def centroid(self) -> Point2D:
        return self._centroid

    @property
    def potential_drop_envelopes(self) -> List[PotentialDropEnvelopes]:
        return self._potential_drop_envelopes

    def shapeable_collection(self) -> List[ShapeableCollection]:
        return self.potential_drop_envelopes
