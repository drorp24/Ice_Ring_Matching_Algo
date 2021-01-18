import unittest
from random import Random

from geometry.distribution.geo_distribution import UniformPointInBboxDistribution, MultiPointInBboxDistribution, \
    ExactPointLocationDistribution
from geometry.geo_factory import create_polygon_2d, create_point_2d


class BasicPointTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pd1 = UniformPointInBboxDistribution(min_x=0, max_x=10, min_y=0, max_y=20)
        cls.pd2 = UniformPointInBboxDistribution(min_x=1000, max_x=1010, min_y=1000, max_y=1020)
        cls.mpd = MultiPointInBboxDistribution({cls.pd1: 0.8, cls.pd2: 0.2})

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
