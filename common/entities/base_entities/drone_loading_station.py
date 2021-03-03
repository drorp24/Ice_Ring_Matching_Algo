from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.entity_id import EntityID
from geometry.geo2d import Point2D
from geometry.geo_factory import convert_dict_to_point_2d


class DroneLoadingStation(JsonableBaseEntity):

    def __init__(self,id:EntityID, location: Point2D):
        self._id=id
        self._location = location

    @property
    def id(self) -> EntityID:
        return self._id

    @property
    def location(self) -> Point2D:
        return self._location

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self.location == other.location and \
               self.id == other.id

    def __hash__(self):
        return hash(self._location)

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DroneLoadingStation(id=EntityID.dict_to_obj(dict_input['id']),
                                   location=convert_dict_to_point_2d(dict_input['location']))
