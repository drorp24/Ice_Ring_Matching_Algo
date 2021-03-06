from __future__ import annotations

import dataclasses
import json
from abc import abstractmethod
from pathlib import Path
from typing import Union, Type
from uuid import UUID

from common.utils.uuid_utils import convert_uuid_to_str


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
            try:
                return [attribute.__dict__() for i, attribute in enumerate(attribs)]
            except:
                return attribs
        try:
            return attribs.__dict__()
        except:
            return attribs


class JsonableBaseEntity(BaseEntity):
    def to_json(self, file_path: Path = None, sort_keys=True, **kwargs) -> Union[str, None]:
        dict_self = self.__dict__()
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(dict_self, f, sort_keys=sort_keys, **kwargs,ensure_ascii=False)
        else:
            return json.dumps(dict_self, sort_keys=sort_keys, **kwargs,ensure_ascii=False)

    @classmethod
    def from_json(cls: Type[JsonableBaseEntity], file_path: Path):
        obj_dict = cls.json_to_dict(file_path)
        return cls.dict_to_obj(obj_dict)

    @staticmethod
    def json_to_dict(file_path: Path):
        with open(file_path, 'rb') as f:
            return json.load(f)

    @classmethod
    @abstractmethod
    def dict_to_obj(cls, dict_input):
        raise NotImplementedError
