from __future__ import annotations

from enum import Enum


class Package:

    def __init__(self, weight: float):
        self._weight = weight

    @property
    def weight(self) -> float:
        return self._weight


class PackageType(Enum):
    TINY = Package(1)
    SMALL = Package(2)
    MEDIUM = Package(4)
    LARGE = Package(8)
