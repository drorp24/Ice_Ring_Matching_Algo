import unittest
from random import Random
from typing import List

import matplotlib.pyplot as plt

from common.entities.distribution.distribution import Range
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, MultiPointInBboxDistribution, \
    ExactPointLocationDistribution, UniformPointsInPolygonDistribution, NormalPointInPolygonDistribution, \
    NormalPointsInMultiPolygonDistribution
from geometry.geo2d import Point2D
from geometry.geo_factory import create_polygon_2d, create_point_2d, create_multipolygon_2d


class BasicPointTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.polygon1 = create_polygon_2d([create_point_2d(0, 0),
                                          create_point_2d(0, 100),
                                          create_point_2d(100, 100),
                                          create_point_2d(100, 0)])

        cls.polygon2 = create_polygon_2d([create_point_2d(0, 0),
                                          create_point_2d(0, 50),
                                          create_point_2d(1, 1),
                                          create_point_2d(50, 50),
                                          create_point_2d(50, 0),
                                          create_point_2d(1, 1),
                                          create_point_2d(0, 0)])

        cls.polygon3 = create_polygon_2d([create_point_2d(100, 100),
                                          create_point_2d(100, 200),
                                          create_point_2d(200, 200),
                                          create_point_2d(200, 100)])

        cls.multi_polygon1 = create_multipolygon_2d([cls.polygon1, cls.polygon3])

        cls.pd1 = UniformPointInBboxDistribution(min_x=0, max_x=10, min_y=0, max_y=20)
        cls.pd2 = UniformPointInBboxDistribution(min_x=1000, max_x=1010, min_y=1000, max_y=1020)
        cls.mpd = MultiPointInBboxDistribution({cls.pd1: 0.8, cls.pd2: 0.2})

        cls.ppd = UniformPointsInPolygonDistribution(cls.polygon1)
        cls.nppd = NormalPointInPolygonDistribution(cls.polygon1, cls.polygon1.calc_centroid())
        cls.npmpd = NormalPointsInMultiPolygonDistribution(multi_polygon=cls.multi_polygon1,
                                                           max_centroids_per_polygon=3)
        cls.npmpd_range = NormalPointsInMultiPolygonDistribution(multi_polygon=cls.multi_polygon1,
                                                                 max_centroids_per_polygon=Range(1, 3))

    def test_sampling_uniform_points_in_bbox(self):
        points = self.pd1.choose_rand(Random(42), 100)
        bbox = create_polygon_2d([create_point_2d(0, 0),
                                  create_point_2d(0, 20),
                                  create_point_2d(10, 20),
                                  create_point_2d(10, 0)])
        self.assertTrue(all([p in bbox for p in points]))

    def test_sampling_multi_uniform_points_in_bbox(self):
        points = self.mpd.choose_rand(Random(42), 100)

        bbox_1 = create_polygon_2d([create_point_2d(0, 0),
                                    create_point_2d(0, 20),
                                    create_point_2d(10, 20),
                                    create_point_2d(10, 0)])

        bbox_2 = create_polygon_2d([create_point_2d(1000, 1000),
                                    create_point_2d(1000, 1020),
                                    create_point_2d(1010, 1020),
                                    create_point_2d(1010, 1000)])

        num_in_bbox_1 = len(list(filter(lambda p: p in bbox_1, points)))
        num_in_bbox_2 = len(list(filter(lambda p: p in bbox_2, points)))

        self.assertEqual(num_in_bbox_1 / len(points), 0.8)
        self.assertEqual(num_in_bbox_2 / len(points), 0.2)

    def test_sampling_exact_point_locations(self):
        expected_point_1 = create_point_2d(0, 0)
        expected_point_2 = create_point_2d(0, 20)
        expected_point_3 = create_point_2d(0, 40)
        exact_pd = ExactPointLocationDistribution([expected_point_1,
                                                   expected_point_2,
                                                   expected_point_3])
        actual_point_1 = exact_pd.choose_rand(Random(42), 1)
        actual_points_2_3 = exact_pd.choose_rand(Random(42), 2)
        self.assertEqual([expected_point_1], actual_point_1)
        self.assertEqual([expected_point_2, expected_point_3], actual_points_2_3)
        self.assertRaises(RuntimeError, exact_pd.choose_rand, (Random(42), 1))

    def test_sampling_uniform_points_in_polygon(self):
        points = self.ppd.choose_rand(Random(42), 200)
        self.assertTrue(all([p in self.polygon1 for p in points]))

    def test_sampling_uniform_points_not_in_polygon(self):
        points = self.ppd.choose_rand(Random(42), 200)
        self.assertTrue(any([p not in self.polygon2 for p in points]))

    def test_sampling_normal_points_in_polygon(self):
        points = self.nppd.choose_rand(Random(42), 200)
        self.assertTrue(all([p in self.polygon1 for p in points]))

    def test_sampling_normal_points_in_multi_polygon(self):
        points = self.npmpd.choose_rand(Random(42), 100)
        self.assertTrue(all([p in self.polygon1 or self.polygon3 for p in points]))

    def test_sampling_normal_points_in_multi_polygon_given_range(self):
        points = self.npmpd_range.choose_rand(Random(42), 100)
        self.assertTrue(all([p in self.polygon1 or self.polygon3 for p in points]))

    @staticmethod
    def _plot_points_distribution(self, points: List[Point2D]):
        x = [p.x for p in points]
        y = [p.y for p in points]
        fig, ax = plt.subplots()
        ax.scatter(x, y)
        plt.show()
