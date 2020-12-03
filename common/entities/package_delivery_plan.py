from __future__ import annotations

from random import Random
from typing import List
from uuid import UUID

from common.entities.base_entity import JsonableBaseEntity
from common.entities.disribution.distribution import Distribution
from common.entities.package import PackageType, PackageDistribution
from common.math.angle import Angle, AngleUniformDistribution, AngleUnit
from geometry.geo2d import Point2D, Polygon2D
from geometry.geo_distribution import UniformPointInBboxDistribution, PointLocationDistribution, \
    DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo_factory import create_polygon_2d_from_ellipse, convert_dict_to_point_2d, create_point_2d
from common.utils.uuid_utils import convert_str_to_uuid
from geometry.geo2d import Point2D
from geometry.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import convert_dict_to_point_2d
from geometry.utils import Localizable


class PackageDeliveryPlan(JsonableBaseEntity, Localizable):

    def __init__(self, id: UUID, drop_point: Point2D, azimuth: Angle, pitch: Angle, package_type: PackageType):
        self._id = id
        self._drop_point = drop_point
        self._azimuth = azimuth
        self._pitch = pitch
        self._package_type = package_type

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    @property
    def azimuth(self) -> Angle:
        return self._azimuth

    @property
    def pitch(self) -> Angle:
        return self._pitch

    @property
    def package_type(self) -> PackageType:
        return self._package_type

    def calc_location(self) -> Point2D:
        return self.drop_point

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return PackageDeliveryPlan(id=convert_str_to_uuid(dict_input['id']),
                                   drop_point=convert_dict_to_point_2d(dict_input['drop_point']),
                                   azimuth=Angle.dict_to_obj(dict_input['azimuth']),
                                   pitch=Angle.dict_to_obj(dict_input['pitch']),
                                   package_type=PackageType.dict_to_obj(dict_input['package_type']))

    def __hash__(self):
        return hash((self.id, self.drop_point, self.azimuth, self.pitch, self.package_type))

    def __str__(self):
        return 'Package Delivery Plan: ' + str((self.id, self.drop_point, self.azimuth, self.pitch, self.package_type))

    def __eq__(self, other):
        return (self.id == other.id) and \
               (self.drop_point == other.drop_point) and \
               (self.azimuth == other.azimuth) and \
               (self.pitch == other.pitch) and \
               (self.package_type == other.package_type)


DEFAULT_AZI_DISTRIB = AngleUniformDistribution(Angle(0, AngleUnit.DEGREE), Angle(355, AngleUnit.DEGREE))
DEFAULT_PITCH_DISTRIB = AngleUniformDistribution(Angle(30, AngleUnit.DEGREE), Angle(90, AngleUnit.DEGREE))
DEFAULT_PACKAGE_DISTRIB = PackageDistribution()


class PackageDeliveryPlanDistribution(Distribution):

    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 azimuth_distribution: AngleUniformDistribution = DEFAULT_AZI_DISTRIB,
                 pitch_distribution: AngleUniformDistribution = DEFAULT_PITCH_DISTRIB,
                 package_type_distribution: PackageDistribution = DEFAULT_PACKAGE_DISTRIB):
        self._relative_drop_point_distribution = relative_location_distribution
        self._azimuth_distribution = azimuth_distribution
        self._pitch_distribution = pitch_distribution
        self._package_type_distribution = package_type_distribution

    def choose_rand(self, random: Random,
                    base_loc: Point2D = create_point_2d(0, 0), amount: int = 1) -> List[PackageDeliveryPlan]:
        relative_drop_points = self._relative_drop_point_distribution.choose_rand(random=random, amount=amount)
        azimuths = self._azimuth_distribution.choose_rand(random=random, amount=amount)
        pitches = self._pitch_distribution.choose_rand(random=random, amount=amount)
        packages = self._package_type_distribution.choose_rand(random=random, amount=amount)
        return [PackageDeliveryPlan(drop_point=dp + base_loc, azimuth=az, pitch=ptc, package_type=p_t) for
                (dp, az, ptc, p_t) in zip(relative_drop_points, azimuths, pitches, packages)]
