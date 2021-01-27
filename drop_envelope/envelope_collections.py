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


class PotentialEnvelopeCollection:

    @abstractmethod
    def shapeable_collection(self) -> List[ShapeableCollection]:
        raise NotImplementedError

    @abstractmethod
    def centroid(self) -> Point2D:
        raise NotImplementedError


def get_farest_shapeable(external_point: Point2D, potential_envelope: List[ShapeableCollection]) -> Shapeable:
    distantest_shapeables = []
    distances = []
    for collection in potential_envelope:
        shapeable_distances = list(map(lambda shapeable:
                                       external_point.calc_distance_to_point(shapeable.calc_location()),
                                       collection.shapeabls()))
        distances.append(max(shapeable_distances))
        distantest_shapeables.append(collection.shapeabls()[shapeable_distances.index(max(shapeable_distances))])
    return distantest_shapeables[distances.index(max(distances))]
