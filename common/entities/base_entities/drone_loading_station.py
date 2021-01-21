from common.entities.base_entities.base_entity import JsonableBaseEntity
from geometry.geo2d import Point2D, EmptyGeometry2D
from geometry.geo_factory import convert_dict_to_point_2d, create_empty_geometry_2d
from geometry.utils import Shapeable


class DroneLoadingStation(JsonableBaseEntity, Shapeable):

    def __init__(self, location: Point2D):
        self._location = location

    @property
    def location(self) -> Point2D:
        return self._location

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.location == other.location

    def __hash__(self):
        return hash(self._location)

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DroneLoadingStation(location=convert_dict_to_point_2d(dict_input['location']))

    def calc_location(self) -> Point2D:
        return self.location

    def get_shape(self) -> EmptyGeometry2D:
        return create_empty_geometry_2d()

    def calc_area(self) -> float:
        return 0

