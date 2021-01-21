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
