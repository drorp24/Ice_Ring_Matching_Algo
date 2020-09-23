from __future__ import annotations

from abc import ABC
import copy


class Package(ABC):

    @property
    def type(self) -> str:
        raise NotImplementedError()

    @property
    def weight_kg(self) -> float:
        raise NotImplementedError()

    def clone(self):
        pass


class _TinyPackage(Package):

    def __init__(self):
        self._type = "Tiny"
        self._weight_kg = 1

    def type(self) -> str:
        return self._type

    def weight_kg(self) -> float:
        return self._weight_kg

    def clone(self):
        return copy.copy(self)


class _SmallPackage(Package):

    def __init__(self):
        self._type = "Small"
        self._weight_kg = 2

    def type(self) -> str:
        return self._type

    def weight_kg(self) -> float:
        return self._weight_kg

    def clone(self):
        return copy.copy(self)


class _MediumPackage(Package):

    def __init__(self):
        self._type = "Medium"
        self._weight_kg = 4

    def type(self) -> str:
        return self._type

    def weight_kg(self) -> float:
        return self._weight_kg

    def clone(self):
        return copy.copy(self)


class _LargePackage(Package):

    def __init__(self):
        self._type = "Large"
        self._weight_kg = 8

    def type(self) -> str:
        return self._type

    def weight_kg(self) -> float:
        return self._weight_kg

    def clone(self):
        return copy.copy(self)


