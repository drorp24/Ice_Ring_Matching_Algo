import itertools
from abc import abstractmethod
from random import Random, randint
from typing import List, Union

from common.entities.distribution.distribution import Distribution, UniformDistribution, Range, ChoiceDistribution, \
    UniformChoiceDistribution
from geometry.geo2d import Point2D, Polygon2D, MultiPolygon2D
from geometry.geo_factory import create_point_2d


class PointLocationDistribution(Distribution):

    @abstractmethod
    def choose_rand(self, random: Random, amount: int) -> List[Point2D]:
        pass

    @classmethod
    def distribution_class(cls) -> type:
        return Point2D


class ExactPointLocationDistribution(PointLocationDistribution):

    def __init__(self, points: List[Point2D]):
        self._points = points
        self._amount_count = 0

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        if self._amount_count + amount > len(self._points):
            raise RuntimeError(
                f"Used {self._amount_count} randomized choices which is \
                more than the initially given {len(self._points)} ")
        choices = self._points[self._amount_count: self._amount_count + amount]
        self._amount_count += amount
        return choices


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


class UniformPointsInPolygonDistribution(PointLocationDistribution):

    def __init__(self, polygon: Polygon2D):
        self._polygon = polygon

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        poly_bbox = self._polygon.calc_bbox()
        distribution = UniformPointInBboxDistribution(min_x=poly_bbox.min_x,
                                                      max_x=poly_bbox.max_x,
                                                      min_y=poly_bbox.min_y,
                                                      max_y=poly_bbox.max_y)

        chosen_points = []
        while len(chosen_points) < amount:
            point = distribution.choose_rand(random)[0]
            if point in self._polygon:
                chosen_points.append(point)

        return chosen_points


class NormalPointsInMultiPolygonDistribution(PointLocationDistribution):

    def __init__(self, multi_polygon: MultiPolygon2D, max_centroids_per_polygon: Union[int, Range] = 1,
                 sigma_x: float = 1, sigma_y: float = 1):
        self._multi_polygon = multi_polygon
        self._max_centroids_per_polygon = max_centroids_per_polygon
        self._sigma_x = sigma_x
        self._sigma_y = sigma_y

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        centroids_per_polygon = randint(int(self._max_centroids_per_polygon.start),
                                        int(self._max_centroids_per_polygon.stop)) if isinstance(
            self._max_centroids_per_polygon, Range) else self._max_centroids_per_polygon

        polygon_centroids_dict = {
            polygon_idx: UniformPointsInPolygonDistribution(polygon_obj).choose_rand(random, centroids_per_polygon)
            for polygon_idx, polygon_obj in enumerate(self._multi_polygon.to_polygons())}

        chosen_polygons_idx = [UniformChoiceDistribution(list(polygon_centroids_dict.keys())).choose_rand(random)[0]
                               for _ in range(amount)]

        chosen_centers = [UniformChoiceDistribution(polygon_centroids_dict[chosen_polygon_idx]).choose_rand(random)[0]
                          for chosen_polygon_idx in chosen_polygons_idx]

        return [NormalPointInPolygonDistribution(polygon=self._multi_polygon.to_polygons()[chosen_polygons_idx],
                                                 center_point=chosen_center, sigma_x=self._sigma_x,
                                                 sigma_y=self._sigma_y).choose_rand(
            random=random)[0]
                for (chosen_polygons_idx, chosen_center) in zip(chosen_polygons_idx, chosen_centers)]


class NormalPointDistribution(PointLocationDistribution):

    def __init__(self, center_point: Point2D, sigma_x: float = 1, sigma_y: float = 1):
        self._center_point = center_point
        self._sigma_x = sigma_x
        self._sigma_y = sigma_y

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        x_list = [random.normalvariate(self._center_point.x, self._sigma_x) for _ in range(amount)]
        y_list = [random.normalvariate(self._center_point.y, self._sigma_y) for _ in range(amount)]
        return [create_point_2d(x, y) for (x, y) in zip(x_list, y_list)]


class NormalPointInPolygonDistribution(NormalPointDistribution):

    def __init__(self, polygon: Polygon2D, center_point: Point2D, sigma_x: float = 1, sigma_y: float = 1):
        super().__init__(center_point, sigma_x, sigma_y)
        self._polygon = polygon

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:

        chosen_points = []
        while len(chosen_points) < amount:
            point = super().choose_rand(random)[0]
            if point in self._polygon:
                chosen_points.append(point)

        return chosen_points


class MultiPointInBboxDistribution(PointLocationDistribution):

    def __init__(self, point_dist_to_prob: dict):
        self._point_dist_to_prob = point_dist_to_prob

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        selected_point_distributions = ChoiceDistribution(self._point_dist_to_prob).choose_rand(random, amount)
        return [spd.choose_rand(random)[0] for spd in selected_point_distributions]


class MultiNormalPointDistribution(PointLocationDistribution):
    def __init__(self, center_points: [Point2D], sigma_x_range: Range = Range(0, 1),
                 sigma_y_range: Range = Range(0, 1)):
        self._centers = center_points
        self._sigma_x_distribution = UniformDistribution(sigma_x_range)
        self._sigma_y_distribution = UniformDistribution(sigma_y_range)

    def choose_rand(self, random: Random, amount: int = 1) -> List[Point2D]:
        all_points = [NormalPointDistribution(center_point=center,
                                              sigma_x=self._sigma_x_distribution.choose_rand(random, 1)[0],
                                              sigma_y=self._sigma_y_distribution.choose_rand(random, 1)[
                                                  0]).choose_rand(
            random, int(amount / len(self._centers))) for center in self._centers]

        return list(itertools.chain.from_iterable(all_points))


class ChoiceNormalPointDistribution(PointLocationDistribution):

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


DEFAULT_ZERO_LOCATION_DISTRIBUTION = UniformPointInBboxDistribution(0, 0, 0, 0)
