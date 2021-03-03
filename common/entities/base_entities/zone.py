from common.entities.base_entities.base_entity import JsonableBaseEntity
from geometry.geo2d import Polygon2D
from geometry.shapely_wrapper import _ShapelyPolygon2D
from common.entities.base_entities.entity_id import EntityID


class Zone(JsonableBaseEntity):

    def __init__(self, region: Polygon2D,id:EntityID):
        self._region = region
        self._id=id

    @property
    def region(self) -> Polygon2D:
        return self._region

    @property
    def id(self) -> EntityID:
        return self._id

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return Zone(_ShapelyPolygon2D.dict_to_obj(dict_input["region"]),
                    EntityID.dict_to_obj(dict_input["id"]))

    def __eq__(self, other):
        return self.region.points == other.region.points
