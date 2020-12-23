from typing import List

from common.entities.distribution.distribution import UniformChoiceDistribution


class PriorityDistribution(UniformChoiceDistribution):
    def __init__(self, priorities: List[float]):
        super().__init__(priorities)

    def distribution_class(self) -> type:
        return float
