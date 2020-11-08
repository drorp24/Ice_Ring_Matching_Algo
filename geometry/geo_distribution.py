from random import Random

from common.entities.base_entities.distribution import Distribution, UniformDistribution, Range, ChoiceDistribution
from geometry.geo_factory import create_point_2d

class PointDistribution(Distribution):

    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float):
        self._min_x = min_x  # TODO: refactor with Bounding Box
        self._min_y = min_y
        self._max_x = max_x
        self._max_y = max_y

    def choose_rand(self, random: Random, number_of_instances: int = 1):
        x_range = Range(self._min_x, self._max_x)
        y_range = Range(self._min_y, self._max_y)
        x_list = UniformDistribution(x_range).choose_rand(random, number_of_instances)
        y_list = UniformDistribution(y_range).choose_rand(random, number_of_instances)
        return [create_point_2d(x, y) for (x, y) in zip(x_list, y_list)]


class MultiPointDistribution(ChoiceDistribution):

    def __init__(self, point_dist_to_prob: dict):
        self._point_dist_to_prob = point_dist_to_prob

    def choose_rand(self, random: Random, amount: int = 1):
        selected_point_distribution: PointDistribution = \
            ChoiceDistribution(self._point_dist_to_prob).choose_rand(random, amount)
        return selected_point_distribution.choose_rand(random)
