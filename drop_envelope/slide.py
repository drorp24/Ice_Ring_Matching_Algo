from abc import ABC
from dataclasses import dataclass
from typing import Union

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from geometry.geo2d import Polygon2D, EmptyGeometry2D, Point2D
from geometry.geo_factory import create_zero_point_2d
from geometry.utils import Localizable
from services.envelope_services_interface import EnvelopeServicesInterface


@dataclass
class SlideProperties:
    package_type: PackageType
    drone_azimuth: Angle
    drop_azimuth: Angle


class Slide(Localizable):
    def __init__(self, slide_properties: SlideProperties, envelope_service: EnvelopeServicesInterface):
        self._package_type = slide_properties.package_type
        self._drone_azimuth = slide_properties.drone_azimuth
        self._drop_azimuth = slide_properties.drop_azimuth
        self._internal_envelope = envelope_service.calc_drop_envelope(slide_properties.package_type,
                                                                      slide_properties.drone_azimuth,
                                                                      create_zero_point_2d(),
                                                                      slide_properties.drop_azimuth)

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    @property
    def drone_azimuth(self) -> Angle:
        return self._drone_azimuth

    @property
    def drop_azimuth(self) -> Angle:
        return self._drop_azimuth

    @property
    def internal_graph(self) -> Union[Polygon2D, EmptyGeometry2D]:
        return self._internal_envelope

    def __repr__(self):
        return "Slide ({0} {1} {2} {3})".format(self.package_type,
                                                self.drone_azimuth.degrees,
                                                self.drop_azimuth.degrees,
                                                self._internal_envelope if self._internal_envelope.__class__ is Polygon2D
                                                else
                                                "EmptyGeometry2D")

    def __eq__(self, other):
        return (self.package_type == other.package_type) and \
               (self.drone_azimuth == other.drone_azimuth) and \
               (self.drop_azimuth == other.drop_azimuth) and \
               (self._internal_envelope == other.internal_envelope)

    def calc_location(self) -> Point2D:
        return self._internal_envelope.centroid

    def shift(self, drop_point: Point2D) -> Union[Polygon2D, EmptyGeometry2D]:
        if self.__class__ is not EmptyGeometry2D:
            return self._internal_envelope.shift(drop_point)
        return EmptyGeometry2D()
