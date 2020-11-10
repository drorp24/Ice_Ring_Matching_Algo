from __future__ import annotations

import json
from abc import abstractmethod

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
        if isinstance(attribs, list):
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
        # for k, v in dict_input.items():
        #     if isinstance(v, dict) and k not in ('__class__', '__enum__'):
        #         dict_input[k] = JsonableBaseEntity.dict_to_obj(v)
        # class_key = dict_input.pop('__class__', None)
        # if class_key is None:
        #     class_key = dict_input.pop('__enum__', None)
        #     split_class_name = class_key.split('.')
        #     return namedtuple(split_class_name[0], split_class_name[1])
        # return namedtuple(class_key, dict_input, rename=True)(*dict_input.values())
