from abc import ABC, abstractmethod
from typing import List

from geometry.geo2d import Point2D
from geometry.utils import Shapeable


class ShapeableCollection:

    @abstractmethod
    def shapeabls(self) -> List[Shapeable]:
        raise NotImplementedError

    @abstractmethod
    def centroid(self) -> Point2D:
        raise NotImplementedError

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

    def __iter__(self):
        return PotentialEnvelopeCollectionIterator(self)

    def __getitem__(self, shapeable_collection_index) -> ShapeableCollection:
        assert shapeable_collection_index >=0 or shapeable_collection_index < len(self.shapeable_collection())
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

    # distantest_shapeables = []
    # distances = []
    # for collection in potential_envelope:
    #     shapeable_distances = list(map(lambda shapeable:
    #                                    external_point.calc_distance_to_point(shapeable.calc_location()),
    #                                    collection.shapeabls()))
    #     distances.append(max(shapeable_distances))
    #     distantest_shapeables.append(collection.shapeabls()[shapeable_distances.index(max(shapeable_distances))])
    # return distantest_shapeables[distances.index(max(distances))]
    distances = list(
        map(lambda collection: max(list(
            map(lambda shapeable: external_point.calc_distance_to_point(shapeable.calc_location()),collection))),
            potential_envelope_collection))
    return max(distances)

