from typing import List

from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from drop_envelope.envelope_collections import PotentialEnvelopeCollection, ShapeableCollection
from geometry.geo2d import Point2D


class LoadingDockPotentialEnvelope(PotentialEnvelopeCollection):

    def __init__(self, drone_loading_dock: DroneLoadingDock):
        self._loading_dock = drone_loading_dock

    def __hash__(self):
        return hash(self.loading_dock)

    def __eq__(self, other):
        return self.loading_dock == other.loading_dock

    @property
    def loading_dock(self) -> DroneLoadingDock:
        return self._loading_dock

    def get_shapeable_collection(self) -> List[ShapeableCollection]:
        return [self.loading_dock]

    def get_centroid(self) -> Point2D:
        return self.loading_dock.calc_location()
