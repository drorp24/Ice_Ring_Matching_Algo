from __future__ import annotations

import json
from abc import abstractmethod, ABC

from geometry.geo2d import Point2D

DEFAULT_TEST_FILE_JSON = 'jsons/test_file.json'


class BaseEntity(object):

    def __repr__(self):
        return str(self.__dict__())

    def __dict__(self):
        d = {member: self.internal_dict(member) for member in dir(self) if
             not member.startswith('_') and not callable(getattr(self, member))}
        d.update({'__class__': type(self).__name__})
        return d

    def internal_dict(self, member):
        attribs = self.__getattribute__(member)
        if isinstance(attribs, list) or isinstance(attribs, set):
            return [attribute.__dict__() for i, attribute in enumerate(attribs)]
        try:
            return attribs.__dict__()
        except:
            return attribs


class JsonableBaseEntity(BaseEntity):

    def to_json(self, file_path: str = DEFAULT_TEST_FILE_JSON):
        with open(file_path, 'w') as f:
            dict_self = self.__dict__()
            json.dump(dict_self, f, sort_keys=True)

    @staticmethod
    def json_to_dict(file_path: str = DEFAULT_TEST_FILE_JSON):
        with open(file_path, 'rb') as f:
            return json.load(f)

    @classmethod
    @abstractmethod
    def dict_to_obj(cls, dict_input):
        raise NotImplementedError


class Localizable(ABC):

    @abstractmethod
    def calc_location(self) -> Point2D:
        raise NotImplementedError
