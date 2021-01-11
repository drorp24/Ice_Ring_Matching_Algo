from common.entities.base_entities.base_entity import JsonableBaseEntity
from geometry.geo2d import Point2D
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import convert_dict_to_point_2d

DEFAULT_LOADING_STATION_LOCATION_DISTRIB = UniformPointInBboxDistribution(0, 100, 0, 100)


class DroneLoadingStation(JsonableBaseEntity):

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
        return DroneLoadingStation(convert_dict_to_point_2d(dict_input['location']))
