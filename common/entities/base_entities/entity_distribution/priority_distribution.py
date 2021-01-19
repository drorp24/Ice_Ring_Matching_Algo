from random import Random
from typing import List

from common.entities.distribution.distribution import UniformChoiceDistribution


class PriorityDistribution(UniformChoiceDistribution):
    def __init__(self, priorities: List[float]):
        super().__init__(priorities)

    @classmethod
    def distribution_class(cls) -> type:
        return float


class ExactPriorityDistribution(PriorityDistribution):
    def __init__(self, priorities=List[float]):
        super().__init__(priorities)
        self._amount_count = 0

    def choose_rand(self, random: Random, amount: int = 1) -> List[float]:
        if self._amount_count + amount > len(self._values):
            raise RuntimeError(
                f"Used {self._amount_count} randomized choices which is \
                more than the initially given {len(self._values)} ")
        choices = self._values[self._amount_count: self._amount_count + amount]
        self._amount_count += amount
        return choices

    @classmethod
    def distribution_class(cls) -> type:
        return float
