from abc import ABC, abstractmethod
from typing import List

from common.math.angle import Angle, AngleUnit
from drop_envelope.arrival_envelope import PotentialArrivalEnvelope, ArrivalEnvelope
from geometry.geo2d import Point2D
from geometry.utils import Shapeable


class ShapeableCollection:

    @abstractmethod
    def shapeabls(self) -> List[Shapeable]:
        raise NotImplementedError

    @abstractmethod
    def centroid(self) -> Point2D:
        raise NotImplementedError

    def get_shapeabls_centroids(self) -> List[Point2D]:
        centroids = [shapeable.calc_location() for shapeable in self.shapeabls()]
        return centroids

    def __iter__(self):
        return ShapeableCollectionIterator(self)

    def __getitem__(self, shpaeable_index) -> Shapeable:
        assert shpaeable_index >= 0 or shpaeable_index < len(self.shapeabls())
        return self.shapeabls()[shpaeable_index]


class ShapeableCollectionIterator:
    def __init__(self, shapeable_collection: ShapeableCollection):
        self._shapeable_collection = shapeable_collection
        self._index = 0

    def __next__(self) -> Shapeable:
        if self._index < len(self._shapeable_collection.shapeabls()):
            result = self._shapeable_collection.shapeabls()[self._index]
            self._index += 1
            return result
        raise StopIteration


class PotentialEnvelopeCollection:

    @abstractmethod
    def shapeable_collection(self) -> List[ShapeableCollection]:
        raise NotImplementedError

    @abstractmethod
    def centroid(self) -> Point2D:
        raise NotImplementedError

    def get_potential_arrival_envelope(self, arrival_azimuths: List[Angle], maneuver_angle: Angle) -> \
            PotentialArrivalEnvelope:
        centroid = self.centroid()
        max_radius = get_max_distance(external_point=centroid,
                                      potential_envelope_collection=self)
        centroid_collection = [collection.get_shapeabls_centroids() for collection in self.shapeable_collection()]
        arrival_envelopes = list(filter(lambda arrival_envelope: arrival_envelope.contains_all(centroid_collection),
                                        map(lambda arrival_azimuth:
                                            ArrivalEnvelope.from_maneuver_angle(centroid=centroid,
                                                                                radius=max_radius,
                                                                                arrival_azimuth=arrival_azimuth,
                                                                                maneuver_angle=maneuver_angle),
                                            arrival_azimuths)))
        return PotentialArrivalEnvelope(arrival_envelopes=arrival_envelopes, centroid=centroid)

    def __iter__(self):
        return PotentialEnvelopeCollectionIterator(self)

    def __getitem__(self, shapeable_collection_index) -> ShapeableCollection:
        assert shapeable_collection_index >= 0 or shapeable_collection_index < len(self.shapeable_collection())
        return self.shapeable_collection()[shapeable_collection_index]


class PotentialEnvelopeCollectionIterator:
    def __init__(self, potential_envelope_collection: PotentialEnvelopeCollection):
        self._potential_envelope_collection = potential_envelope_collection
        self._index = 0

    def __next__(self) -> ShapeableCollection:
        if self._index < len(self._potential_envelope_collection.shapeable_collection()):
            result = self._potential_envelope_collection.shapeable_collection()[self._index]
            self._index += 1
            return result
        raise StopIteration


def get_max_distance(external_point: Point2D, potential_envelope_collection: PotentialEnvelopeCollection) -> float:
    distances = list(
        map(lambda collection: max(list(
            map(lambda shapeable: external_point.calc_distance_to_point(shapeable.calc_location()), collection))),
            potential_envelope_collection))
    return max(distances)
