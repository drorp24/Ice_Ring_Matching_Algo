from copy import deepcopy

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.entity_id import EntityID
from geometry.geo2d import Point2D
from geometry.geo_factory import convert_dict_to_point_2d
from geometry.utils import Shapeable


class DroneLoadingStation(JsonableBaseEntity, Shapeable):

    def __init__(self, id_: EntityID, location: Point2D):
        self._id = id_
        self._location = location

    @property
    def id(self) -> EntityID:
        return self._id

    @property
    def location(self) -> Point2D:
        return self._location

    def calc_location(self) -> Point2D:
        return self.location

    def get_shape(self) -> Point2D:
        return self.location

    def calc_area(self) -> float:
        return 0

    def __eq__(self, other):
        return all([self.__class__ == other.__class__,
                   self.id == other.id,
                   self.location == other.location])

    def __hash__(self):
        return hash((self.id, self._location))

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        # noinspection PyArgumentList
        new_copy = DroneLoadingStation(self.id, deepcopy(self.location, memodict))
        memodict[id(self)] = new_copy
        return new_copy

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DroneLoadingStation(id_=EntityID.dict_to_obj(dict_input['id']),
                                   location=convert_dict_to_point_2d(dict_input['location']))
