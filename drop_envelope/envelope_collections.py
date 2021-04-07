from abc import abstractmethod
from typing import List

from common.math.angle import Angle
from drop_envelope.arrival_envelope import PotentialArrivalEnvelope, ArrivalEnvelope
from geometry.geo2d import Point2D
from geometry.utils import Shapeable


class ShapeableCollection:

    @abstractmethod
    def get_shapeables(self) -> List[Shapeable]:
        raise NotImplementedError

    @abstractmethod
    def get_centroid(self) -> Point2D:
        raise NotImplementedError

    def get_shapeables_centroids(self) -> List[Point2D]:
        centroids = [shapeable.calc_location() for shapeable in self.get_shapeables()]
        return centroids

    def __iter__(self):
        return ShapeableCollectionIterator(self)

    def __getitem__(self, shpaeable_index) -> Shapeable:
        assert shpaeable_index >= 0 or shpaeable_index < len(self.get_shapeables())
        return self.get_shapeables()[shpaeable_index]


class ShapeableCollectionIterator:
    def __init__(self, shapeable_collection: ShapeableCollection):
        self._shapeable_collection = shapeable_collection
        self._index = 0

    def __next__(self) -> Shapeable:
        if self._index < len(self._shapeable_collection.get_shapeables()):
            result = self._shapeable_collection.get_shapeables()[self._index]
            self._index += 1
            return result
        raise StopIteration


class PotentialEnvelopeCollection:

    @abstractmethod
    def get_shapeable_collection(self) -> List[ShapeableCollection]:
        raise NotImplementedError

    @abstractmethod
    def get_centroid(self) -> Point2D:
        raise NotImplementedError

    def get_largest_distance_from_centroid(self) -> float:
        distances = list(
            map(lambda collection: max(list(
                map(lambda shapeable: self.get_centroid().calc_distance_to_point(shapeable.calc_location()),
                    collection))),
                self.get_shapeable_collection()))
        return max(distances)

    def get_potential_arrival_envelope(self, arrival_azimuths: List[Angle], maneuver_angle: Angle) -> \
            PotentialArrivalEnvelope:
        centroid = self.get_centroid()
        max_radius = self.get_largest_distance_from_centroid()
        centroid_collection = [collection.get_shapeables_centroids() for collection in self.get_shapeable_collection()]
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
        assert shapeable_collection_index >= 0 or shapeable_collection_index < len(self.get_shapeable_collection())
        return self.get_shapeable_collection()[shapeable_collection_index]


class PotentialEnvelopeCollectionIterator:
    def __init__(self, potential_envelope_collection: PotentialEnvelopeCollection):
        self._potential_envelope_collection = potential_envelope_collection
        self._index = 0

    def __next__(self) -> ShapeableCollection:
        if self._index < len(self._potential_envelope_collection.get_shapeable_collection()):
            result = self._potential_envelope_collection.get_shapeable_collection()[self._index]
            self._index += 1
            return result
        raise StopIteration
