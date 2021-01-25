from common.entities.base_entities.base_entity import JsonableBaseEntity
from geometry.geo2d import Polygon2D
from geometry.shapely_wrapper import _ShapelyPolygon2D


class Zone(JsonableBaseEntity):

    def __init__(self, region: Polygon2D):
        self._region = region

    @property
    def region(self) -> Polygon2D:
        return self._region

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return Zone(_ShapelyPolygon2D.dict_to_obj(dict_input["region"]))

    def __eq__(self, other):
        return self.region == other.region
