from math import cos, sin
from typing import List
from common.math.angle import Angle, AngleUnit
from geometry.geo2d import Point2D, Polygon2D
from geometry.geo_factory import create_point_2d, create_polygon_2d


class ArrivalEnvelope:
    def __init__(self, arrival_azimuth: Angle, repr_point: Point2D, maneuver_polygon: Polygon2D):
        self._arrival_azimuth = arrival_azimuth
        self._repr_point = repr_point
        self._maneuver_polygon = maneuver_polygon

    @classmethod
    def from_maneuver_angle(cls, centroid: Point2D, radius: float, arrival_azimuth: Angle, maneuver_angle: Angle,
                            resolution_parameter: int = 2):
        observation_angle = Angle(value=arrival_azimuth.degrees + 180, unit=AngleUnit.DEGREE)
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
    def maneuver_polygon(self) -> Polygon2D:
        return self._maneuver_polygon


class PotentialArrivalEnvelope:
    def __init__(self, arrival_envelopes: List[ArrivalEnvelope]):
        self._arrival_envelopes = {arrival_envelope.arrival_azimuth: arrival_envelope
                                   for arrival_envelope in arrival_envelopes}

    @property
    def arrival_envelopes(self) -> dict[Angle, ArrivalEnvelope]:
        return self._arrival_envelopes

    def get_arrival_envelope(self, arrival_azimuth: Angle) -> ArrivalEnvelope:
        return self.arrival_envelopes[arrival_azimuth]


