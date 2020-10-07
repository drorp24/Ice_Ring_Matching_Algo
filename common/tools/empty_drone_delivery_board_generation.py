from random import Random

import math
from common.utils import json_file_handler
from common.entities.drone import PlatformType, DroneConfigurationType
from common.entities.drone_formation import DroneFormationType, FormationSize

_fleet_of_platform_types = {PlatformType.PLATFORM_1: 30, PlatformType.PLATFORM_2: 20}
_formation_size_policy = {FormationSize.MINI: 0.5, FormationSize.MEDIUM: 0.5}
_drone_configuration_policy = {PlatformType.PLATFORM_1: {DroneConfigurationType.PLATFORM_1_2X8: 0.4,
                                                         DroneConfigurationType.PLATFORM_1_4X4: 0.4,
                                                         DroneConfigurationType.PLATFORM_1_8X2: 0.1,
                                                         DroneConfigurationType.PLATFORM_1_16X1: 0.1},
                               PlatformType.PLATFORM_2: {DroneConfigurationType.PLATFORM_2_4X8: 0.4,
                                                         DroneConfigurationType.PLATFORM_2_8X4: 0.4,
                                                         DroneConfigurationType.PLATFORM_2_16X2: 0.1,
                                                         DroneConfigurationType.PLATFORM_2_32X1: 0.1}}


def _get_configuration_distribution(platform_type: PlatformType) -> []:
    weights = _drone_configuration_policy[platform_type].values()
    total_weight = sum(weights)
    distribution = [weight / total_weight for weight in weights]
    return distribution


def _get_formation_size_distribution() -> []:
    weights = _formation_size_policy.values()
    total_weight = sum(weights)
    distribution = [weight / total_weight for weight in weights]
    return distribution


def _get_population(distribution: [], platform_type: PlatformType) -> {}:
    fleet_of_platform_type = _fleet_of_platform_types[platform_type]
    population = [math.floor(fleet_of_platform_type * prob) for prob in distribution]
    total_population = sum(population)
    population_gap = fleet_of_platform_type - total_population
    if population_gap > 0:
        max_index = population.index(max(population))
        population[max_index] += population_gap
    platform_configuration_population = _drone_configuration_policy[platform_type]
    for index, key in enumerate(platform_configuration_population.keys()):
        platform_configuration_population[key] = population[index]
    return platform_configuration_population


def _formation_options(platform_type: PlatformType) -> []:
    maximum_formations_of_medium_size = math.floor(PlatformType.PLATFORM_1 / FormationSize.MEDIUM)
    for formation in range()
