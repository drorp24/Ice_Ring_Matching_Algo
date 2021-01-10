from abc import abstractmethod, ABC
from typing import List, Union

from common.math.angle import Angle, NoneAngle
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
    def get_arrival_azimuth(self) -> Union[Angle, NoneAngle]:
        raise NotImplementedError


class PotentialEnvelopeCollection(ABC):
    @abstractmethod
    def get_potential_envelopes(self) -> List[ShapeableCollection]:
        raise NotImplementedError

    @abstractmethod
    def get_centroid(self) -> Point2D:
        raise NotImplementedError
