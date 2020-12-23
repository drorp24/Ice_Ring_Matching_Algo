from typing import List

from common.entities.distribution.distribution import UniformChoiceDistribution


class PriorityDistribution(UniformChoiceDistribution):
    def __init__(self, priorities: List[float]):
        super().__init__(priorities)

    @classmethod
    def distribution_class(cls) -> type:
        return float
