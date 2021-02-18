from uuid import UUID
from typing import Union

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.utils import uuid_utils


class EntityID(JsonableBaseEntity):

    def __init__(self, uuid: Union[UUID,str]):
        self._uuid = uuid
        self._internal_type = uuid.__class__.__name__

    @property
    def uuid(self):
        return self._uuid

    @property
    def internal_type(self):
        return self._internal_type

    @classmethod
    def dict_to_obj(cls, dict_input):
        if dict_input['internal_type'] == 'str':
            return EntityID(dict_input['uuid'])
        if dict_input['internal_type'] =='UUID':
            return EntityID(uuid_utils.convert_str_to_uuid(dict_input['uuid']))

    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return self.uuid == other.uuid
