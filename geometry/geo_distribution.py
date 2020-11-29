from abc import abstractmethod
from random import Random
from typing import List

from common.entities.disribution.distribution import Distribution, UniformDistribution, Range, ChoiceDistribution, \
    UniformChoiceDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d


class PointLocationDistribution(Distribution):

    @abstractmethod
    def choose_rand(self, random: Random, amount: int) -> List[Point2D]:
        pass


class UniformPointInBboxDistribution(PointLocationDistribution):

    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float):
        self._min_x = min_x
        self._min_y = min_y
        self._max_x = max_x
        self._max_y = max_y

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        x_range = Range(self._min_x, self._max_x)
        y_range = Range(self._min_y, self._max_y)
        x_list = UniformDistribution(x_range).choose_rand(random, amount)
        y_list = UniformDistribution(y_range).choose_rand(random, amount)
        return [create_point_2d(x, y) for (x, y) in zip(x_list, y_list)]


class NormalPointDistribution(PointLocationDistribution):

    def __init__(self, center_point: Point2D, sigma_x: float = 1, sigma_y: float = 1):
        self._center_point = center_point
        self._sigma_x = sigma_x
        self._sigma_y = sigma_y

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        x_list = [random.normalvariate(self._center_point.x, self._sigma_x) for _ in range(amount)]
        y_list = [random.normalvariate(self._center_point.y, self._sigma_y) for _ in range(amount)]
        return [create_point_2d(x, y) for (x, y) in zip(x_list, y_list)]


class MultiPointInBboxDistribution(PointLocationDistribution):

    def __init__(self, point_dist_to_prob: dict):
        self._point_dist_to_prob = point_dist_to_prob

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        selected_point_distributions = ChoiceDistribution(self._point_dist_to_prob).choose_rand(random, amount)
        return [spd.choose_rand(random)[0] for spd in selected_point_distributions]


class ChoiceNormalDistribution(PointLocationDistribution):

    def __init__(self, center_points: [Point2D], sigma_x_range: Range = Range(0, 1),
                 sigma_y_range: Range = Range(0, 1)):
        self._center_distrib = UniformChoiceDistribution(center_points)
        self._sigma_x_distrib = UniformDistribution(sigma_x_range)
        self._sigma_y_distrib = UniformDistribution(sigma_y_range)

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        selected_center = self._center_distrib.choose_rand(random, 1)[0]
        return [NormalPointDistribution(selected_center,
                                        self._sigma_x_distrib.choose_rand(random, 1)[0],
                                        self._sigma_y_distrib.choose_rand(random, 1)[0]).choose_rand(random, 1)[0]
                for _ in range(amount)]
