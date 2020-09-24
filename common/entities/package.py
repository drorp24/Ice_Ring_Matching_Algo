from __future__ import annotations

from enum import Enum


class _Package:

    def __init__(self, size: float):
        self._size = size

    @property
    def size(self):
        return self._size


class PackageType(Enum):
    TINY = _Package(1)
    SMALL = _Package(2)
    MEDIUM = _Package(4)
    LARGE = _Package(8)
