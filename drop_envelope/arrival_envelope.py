from math import cos, sin
from typing import List, Dict, Union
from common.math.angle import Angle, AngleUnit
from geometry.geo2d import Point2D, Polygon2D, EmptyGeometry2D
from geometry.geo_factory import create_point_2d, create_polygon_2d, create_empty_geometry_2d
import itertools


class ArrivalEnvelope:
    def __init__(self, arrival_azimuth: Angle, repr_point: Point2D,
                 maneuver_polygon: Union[Polygon2D, EmptyGeometry2D]):
        self._arrival_azimuth = arrival_azimuth
        self._repr_point = repr_point
        self._maneuver_polygon = maneuver_polygon

    @classmethod
    def from_maneuver_angle(cls, centroid: Point2D, radius: float, arrival_azimuth: Angle, maneuver_angle: Angle,
                            resolution_parameter: int = 6):
        observation_angle = Angle(value=arrival_azimuth.degrees + 180, unit=AngleUnit.DEGREE)
        if radius == 0:
            return ArrivalEnvelope(arrival_azimuth=arrival_azimuth,
                                   repr_point=centroid,
                                   maneuver_polygon=create_empty_geometry_2d())

        maneuver_factor = list(map(lambda angle_factor:
                                   1 / (2 * resolution_parameter) * angle_factor,
                                   list(range(-resolution_parameter, resolution_parameter + 1))))
        observation_angles = list(map(lambda factor:
                                      Angle(value=observation_angle.degrees + factor * maneuver_angle.degrees,
                                            unit=AngleUnit.DEGREE), maneuver_factor))
        outer_arcs_points = list(map(lambda angle: create_point_2d(x=centroid.x + radius * cos(angle.radians),
                                                                   y=centroid.y + radius * sin(angle.radians))
                                     , observation_angles))
        return ArrivalEnvelope(arrival_azimuth=arrival_azimuth,
                               repr_point=outer_arcs_points[resolution_parameter],
                               maneuver_polygon=create_polygon_2d([centroid] + outer_arcs_points))

    @property
    def arrival_azimuth(self) -> Angle:
        return self._arrival_azimuth

    @property
    def repr_point(self) -> Point2D:
        return self._repr_point

    @property
    def maneuver_polygon(self) -> Union[Polygon2D, EmptyGeometry2D]:
        return self._maneuver_polygon

    def calc_cost(self, other_arrival_envelope) -> float:
        return self._repr_point.calc_distance_to_point(other_arrival_envelope.repr_point)

    def contains(self, point: Point2D) -> bool:
        if isinstance(self.maneuver_polygon, EmptyGeometry2D):
            return point == self.repr_point
        return self.maneuver_polygon.__contains__(point)

    def contains_any(self, points: List[Point2D]) -> bool:
        if isinstance(self.maneuver_polygon, EmptyGeometry2D):
            return any([self.repr_point == point for point in points])
        return any([self.maneuver_polygon.__contains__(point) for point in points])

    def contains_all(self, points_collection: List[List[Point2D]]) -> bool:
        return all([self.contains_any(points) for points in points_collection])

    def __eq__(self, other):
        return self.repr_point == other.repr_point and self.arrival_azimuth == other.arrival_azimuth and \
               self.maneuver_polygon == other.maneuver_polygon


class PotentialArrivalEnvelope:
    def __init__(self, arrival_envelopes: List[ArrivalEnvelope], centroid: Point2D):
        self._arrival_envelopes = {arrival_envelope.arrival_azimuth: arrival_envelope
                                   for arrival_envelope in arrival_envelopes}
        self._centroid = centroid

    @property
    def arrival_envelopes(self) -> Dict[Angle, ArrivalEnvelope]:
        return self._arrival_envelopes

    @property
    def centroid(self) -> Point2D:
        return self._centroid

    def __eq__(self, other):
        return self.arrival_envelopes == other.arrival_envelopes and self.centroid == other.centroid

    def get_arrival_envelope(self, arrival_azimuth: Angle) -> ArrivalEnvelope:
        return self.arrival_envelopes[arrival_azimuth]


def calc_cost(potential_arrival_envelope_1: PotentialArrivalEnvelope,
              potential_arrival_envelope_2: PotentialArrivalEnvelope) -> float:
    arrival_envelopes_tuples = itertools.product(*[potential_arrival_envelope_1.arrival_envelopes.values(),
                                                   potential_arrival_envelope_2.arrival_envelopes.values()])
    costs = list(map(lambda ar_tuple: ar_tuple[0].calc_cost(ar_tuple[1]) *
                                      (2 - cos(ar_tuple[0].arrival_azimuth.radians -
                                               ar_tuple[1].arrival_azimuth.radians)), arrival_envelopes_tuples))
    return min(costs)
