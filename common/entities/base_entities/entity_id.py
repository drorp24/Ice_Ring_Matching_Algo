from uuid import UUID

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.utils import uuid_utils


class EntityID(JsonableBaseEntity):

    def __init__(self, uuid: UUID):
        self._uuid = uuid

    @property
    def uuid(self):
        return self._uuid

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return EntityID(uuid_utils.convert_str_to_uuid(dict_input['uuid']))

    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return self.uuid == other.uuid
