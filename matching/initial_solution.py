from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from common.entities.base_entities.base_entity import JsonableBaseEntity
from matching.matcher_input import MatcherInput


@dataclass
class Route(JsonableBaseEntity):
    indexes: List[int]

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return Route(dict_input['indexes'])


@dataclass
class Routes(JsonableBaseEntity):
    routes: List[Route]

    def as_list(self) -> List[List[int]]:
        return [[index for index in route.indexes] for route in self.routes]

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return Routes([Route.dict_to_obj(route_dict)
                       for route_dict
                       in dict_input['routes']])


class InitialSolution(ABC):

    def __init__(self, matcher_input: MatcherInput):
        self.matcher_input = matcher_input

    @staticmethod
    @abstractmethod
    def calc() -> Routes:
        raise NotImplementedError()
