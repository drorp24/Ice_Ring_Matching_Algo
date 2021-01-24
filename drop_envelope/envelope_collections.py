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



def get_distantest_shapeable(external_point: Point2D, potential_envelope: List[ShapeableCollection]) -> Shapeable:
    #TODO: Not finished yet
    for i, shapeables in enumerate(potential_envelope):
