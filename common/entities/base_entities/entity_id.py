import uuid
from typing import Union

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.utils import uuid_utils


class EntityID(JsonableBaseEntity):

    def __init__(self, uuid_: Union[uuid.UUID, str]):
        self._uuid = uuid_
        self._internal_type = uuid_.__class__.__name__

    @property
    def uuid(self):
        return self._uuid

    @property
    def internal_type(self):
        return self._internal_type

    @classmethod
    def generate_uuid(cls):
        return EntityID(uuid.uuid4())

    @classmethod
    def dict_to_obj(cls, dict_input):
        if dict_input['internal_type'] == 'str':
            return EntityID(dict_input['uuid'])
        if dict_input['internal_type'] == 'UUID':
            if type(dict_input['uuid']) is str:
                return EntityID(uuid_utils.convert_str_to_uuid(dict_input['uuid']))
            else:
                return dict_input['uuid']

    def display_name(self,amount_chars:int) -> str:
        if len(str(self.uuid)) >= amount_chars:
            return str(self.uuid)[-amount_chars:]

        return str(self.uuid)

    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        new_copy = EntityID(self._uuid)
        memodict[id(self)] = new_copy
        return new_copy
