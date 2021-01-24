from random import Random

from common.entities.base_entities.drone import DroneType
from common.entities.distribution.distribution import Distribution, ChoiceDistribution


class DroneTypeDistribution(Distribution):

    def __init__(self, drone_type_options: {DroneType, int} = None):
        if drone_type_options is None:
            drone_type_options = {drone_type: 1 for drone_type in DroneType}
        self._drone_type_options = drone_type_options

    def choose_rand(self, random: Random, amount: int):
        drone_choice_distribution = ChoiceDistribution(self._drone_type_options)
        return drone_choice_distribution.choose_rand(random, amount)

    @classmethod
    def distribution_class(cls) -> type:
        return DroneType