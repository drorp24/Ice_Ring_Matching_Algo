from abc import ABC, abstractmethod
from typing import Dict


class BaseEntity(ABC, object):

    def __repr__(self):
        return str(self.__dict__())

    def __dict__(self):
        return {member: self.__getattribute__(member) for member in dir(self) if
                not member.startswith('_') and not callable(getattr(self, member))}
