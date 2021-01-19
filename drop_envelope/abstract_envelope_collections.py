from abc import abstractmethod, ABC
from typing import List
from optional import Optional

from common.math.angle import Angle
from geometry.geo2d import Point2D
from geometry.utils import Shapeable


class ShapeableCollection(ABC):
    @abstractmethod
    def get_shapeable_collection(self) -> List[Shapeable]:
        raise NotImplementedError

    @abstractmethod
    def get_centroid(self) -> Point2D:
        raise NotImplementedError

    @abstractmethod
    def get_arrival_azimuth(self) -> Optional.of(Angle):
        raise NotImplementedError


class PotentialEnvelopeCollection(ABC):
    @abstractmethod
    def get_potential_envelopes(self) -> List[ShapeableCollection]:
        raise NotImplementedError

    @abstractmethod
    def get_centroid(self) -> Point2D:
        raise NotImplementedError
