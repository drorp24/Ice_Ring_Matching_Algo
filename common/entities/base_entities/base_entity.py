from __future__ import annotations

import json
from abc import abstractmethod, ABCMeta
from uuid import UUID
import dataclasses
from common.utils.uuid_utils import convert_uuid_to_str

DEFAULT_TEST_FILE_JSON = 'jsons/test_file.jsons'


class BaseEntity(object):

    def __repr__(self):
        return str(self.__dict__())

    def __dict__(self):
        d = {'__class__': type(self).__name__}
        if dataclasses.is_dataclass(self):
            d.update({member: self.internal_dict(member) for member in self.__annotations__.keys()})
        else:
            d.update({member: self.internal_dict(member) for member in dir(self)
                      if not member.startswith('_') and not callable(getattr(self, member))})
        return d

    def internal_dict(self, member):
        attribs = self.__getattribute__(member)
        if isinstance(attribs, UUID):
            return convert_uuid_to_str(attribs)
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

    def from_json(target_class: ABCMeta, file_path: str = DEFAULT_TEST_FILE_JSON):
        obj_dict = target_class.json_to_dict(file_path)
        return target_class.dict_to_obj(obj_dict)

    @staticmethod
    def json_to_dict(file_path: str = DEFAULT_TEST_FILE_JSON):
        with open(file_path, 'rb') as f:
            return json.load(f)

    @classmethod
    @abstractmethod
    def dict_to_obj(cls, dict_input):
        raise NotImplementedError
