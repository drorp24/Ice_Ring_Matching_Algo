from __future__ import annotations

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.math.angle import Angle
from geometry.geo2d import Point2D
from geometry.geo_factory import convert_dict_to_point_2d
from geometry.utils import Localizable


class PackageDeliveryPlan(JsonableBaseEntity, Localizable):

    def __init__(self, id_: EntityID, drop_point: Point2D, azimuth: Angle, pitch: Angle, package_type: PackageType):
        self._id = id_
        self._drop_point = drop_point
        self._azimuth = azimuth
        self._pitch = pitch
        self._package_type = package_type

    @property
    def id(self) -> EntityID:
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
        return PackageDeliveryPlan(id_=EntityID.dict_to_obj(dict_input['id']),
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

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        new_copy = PackageDeliveryPlan(self.id, self.drop_point, self.azimuth, self.pitch, self.package_type)
        memodict[id(self)] = new_copy
        return self
