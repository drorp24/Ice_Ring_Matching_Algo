from abc import ABC, abstractmethod
from typing import Dict


class BaseEntity(ABC, object):

    def __repr__(self):
        return "{klass}, @{id:x}, {attrs} ".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{} = {!r}".format(k, v) for k, v in self.__dict__.items()),
        )


class JSONable(ABC, object):

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_dict(input_dict: Dict):
        raise NotImplementedError
