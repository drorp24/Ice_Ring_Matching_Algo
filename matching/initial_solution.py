from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from matching.matcher_input import MatcherInput


@dataclass
class Route:
    indexes: List[int]


@dataclass
class Routes:
    routes: List[Route]

    def as_list(self) -> List[List[int]]:
        return [[index for index in route.indexes] for route in self.routes]


class InitialSolution(ABC):

    @staticmethod
    @abstractmethod
    def calc(matcher_input: MatcherInput) -> Routes:
        raise NotImplementedError()
