from random import Random

from common.entities.base_entities.drone import PlatformType
from common.entities.distribution.distribution import Distribution, ChoiceDistribution


class PlatformTypeDistribution(Distribution):

    def __init__(self, platform_type_options: {PlatformType, int} = None):
        if platform_type_options is None:
            platform_type_options = {platform_type: 1 for platform_type in PlatformType}
        self._platform_type_options = platform_type_options

    def choose_rand(self, random: Random, amount: int):
        platform_choice_distribution = ChoiceDistribution(self._platform_type_options)
        return platform_choice_distribution.choose_rand(random, amount)

    def distribution_class(self) -> type:
        return PlatformType