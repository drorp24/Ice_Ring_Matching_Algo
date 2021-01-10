from typing import List

from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from drop_envelope.abstract_envelope_collections import PotentialEnvelopeCollection, ShapeableCollection
from geometry.geo2d import Point2D


class DroneLoadingDockPotentialEnvelope(PotentialEnvelopeCollection):
    def __init__(self, drone_loading_dock: DroneLoadingDock):
        self._loading_dock = drone_loading_dock

    @property
    def loading_dock(self) -> DroneLoadingDock:
        return self._loading_dock

    def get_potential_envelopes(self) -> List[ShapeableCollection]:
        return [self.loading_dock]

    def get_centroid(self) -> Point2D:
        return self.loading_dock.get_centroid()
