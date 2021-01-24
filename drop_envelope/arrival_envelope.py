from typing import List, Union

from common.math.angle import Angle
from drop_envelope.envelope_collections import ShapeableCollection, PotentialEnvelopeCollection
from geometry.geo2d import Point2D, Polygon2D, EmptyGeometry2D
from geometry.geo_factory import create_empty_geometry_2d
from geometry.utils import Shapeable


class ArrivalEnvelope(Shapeable):

    def __init__(self, arrival_azimuth: Angle, representation_point: Point2D):
        self._arrival_azimuth = arrival_azimuth
        self._representation_point = representation_point

    @property
    def arrival_azimuth(self) -> Angle:
        return self._arrival_azimuth

    @property
    def representation_point(self) -> Point2D:
        self._representation_point

    def calc_location(self) -> Point2D:
        return self.representation_point

    def get_shape(self) -> Union[Polygon2D, EmptyGeometry2D]:
        return create_empty_geometry_2d()

    def calc_area(self) -> float:
        return 0


class PotentialArrivalEnvelope(ShapeableCollection):

    def __init__(self, arrival_envelopes: List[ArrivalEnvelope], centroid: Point2D):
        self._arrival_envelopes = {arrival_envelope.arrival_azimuth: arrival_envelope
                                  for arrival_envelope in arrival_envelopes}
        self._centroid = centroid

    @classmethod
    def from_potential_envelope_collection(cls, arrival_azimuths: List[Angle],
                                           potential_envelope_collection: PotentialEnvelopeCollection):
        centroid = potential_envelope_collection.centroid()

    @property
    def arrival_envelopes(self) -> dict[Angle, ArrivalEnvelope]:
        return self._arrival_envelopes

    @property
    def centroid(self) -> Point2D:
        return self._centroid

    def shapeabls(self) -> List[Shapeable]:
        return list(self.arrival_envelopes.values())

