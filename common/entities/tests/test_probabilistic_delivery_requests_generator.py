import unittest
from random import Random

import params
from common.entities.package import PackageType
from common.entities.probabilistic_delivery_requests_generator import get_distribution, create_delivery_requests_dict, \
    get_time_window, create_delivery_requests_json, IntRange, WeightedIntRange, IntDistribution, PointDistribution, WeightedPointRange, FloatRange
from input.delivery_requests_json_converter import create_delivery_requests_from_file


class ProbabilisticDeliveryRequestsGenerationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rand = Random()

    def test_get_distribution_list(self):
        distribution = get_distribution([[[0, 359], 1]])
        self.assertEqual(len(distribution), 2)
        self.assertEqual(len(distribution[0]), 360)
        self.assertEqual(distribution[1][0], 1 / 360)
        self.assertAlmostEqual(sum(distribution[1]), 1)

    def test_get_distribution_package(self):
        distribution = get_distribution([[PackageType.TINY.name, 0.5],
                                         [PackageType.SMALL.name, 0.3],
                                         [PackageType.MEDIUM.name, 0.2],
                                         [PackageType.LARGE.name, 0]])
        self.assertEqual(len(distribution), 2)
        self.assertEqual(len(distribution[0]), 4)
        self.assertEqual(distribution[1][0], 0.5)

    def test_get_time_window_one_day_3_hours(self):
        time_window = get_time_window([24, 24], [[[1, 2], 0], [[3, 3], 1]], self.rand)
        self.assertGreater(time_window['end_time']['hour'], time_window['start_time']['hour'])
        self.assertEqual(time_window['end_time']['hour'] - time_window['start_time']['hour'], 3)
        self.assertLessEqual(int(time_window['end_time']['hour']), 24)
        self.assertEqual(time_window['end_time']['day'] - time_window['start_time']['day'], 0)
        self.assertEqual(time_window['start_time']['day'], params.BASE_DAY)

    def test_get_time_window_two_days_28_hours(self):
        time_window = get_time_window([48, 48], [[[28, 28], 1]], self.rand)
        self.assertGreater(time_window['end_time']['day'], time_window['start_time']['day'])
        self.assertEqual(time_window['end_time']['hour'] - time_window['start_time']['hour'] + 24, 28)
        self.assertLessEqual(time_window['end_time']['hour'], 24)
        self.assertEqual(time_window['start_time']['day'], params.BASE_DAY)
        self.assertEqual(time_window['end_time']['day'], params.BASE_DAY + 1)

    def test_create_delivery_requests_with_seed(self):
        num_of_delivery_options_distribution = IntDistribution([WeightedIntRange(1, 2, 1)])
        drop_points_distribution = PointDistribution([
            WeightedPointRange(FloatRange(0.0, 100.0), FloatRange(0.0, 100.0), 0.7),
            WeightedPointRange(FloatRange(100.0, 200.0), FloatRange(0.0, 100.0), 0.3)])

        delivery_request_dict1 = create_delivery_requests_dict(num_of_delivery_requests_range=IntRange(5, 5),
                                                               num_of_delivery_options_distribution=num_of_delivery_options_distribution,
                                                               num_of_customer_deliveries_distribution=[[[1, 3], 0.9],
                                                                                                        [[4, 5], 0.1]],
                                                               num_of_package_delivery_plans_distribution=[
                                                                   [[1, 3], 0.7], [[4, 5], 0.3]],
                                                               main_time_window_length_range=[24, 24],
                                                               time_windows_length_distribution=[[[1, 2], 0.1],
                                                                                                 [[3, 5], 0.3],
                                                                                                 [[5, 15], 0.3],
                                                                                                 [[15, 24], 0.3]],
                                                               priority_distribution=[[[0, 3], 1]],
                                                               drop_points_distribution=drop_points_distribution,
                                                               azimuth_distribution=[[[0, 359], 1]],
                                                               elevation_distribution=[[[90, 90], 0.5],
                                                                                       [[30, 89], 0.5]],
                                                               package_distribution=[[PackageType.TINY.name, 0.5],
                                                                                     [PackageType.SMALL.name, 0.3],
                                                                                     [PackageType.MEDIUM.name, 0.2],
                                                                                     [PackageType.LARGE.name, 0]],
                                                               random_seed=10)
        delivery_request_dict2 = create_delivery_requests_dict(num_of_delivery_requests_range=IntRange(5, 5),
                                                               num_of_delivery_options_distribution=num_of_delivery_options_distribution,
                                                               num_of_customer_deliveries_distribution=[[[1, 3], 0.9],
                                                                                                        [[4, 5], 0.1]],
                                                               num_of_package_delivery_plans_distribution=[
                                                                   [[1, 3], 0.7], [[4, 5], 0.3]],
                                                               main_time_window_length_range=[24, 24],
                                                               time_windows_length_distribution=[[[1, 2], 0.1],
                                                                                                 [[3, 5], 0.3],
                                                                                                 [[5, 15], 0.3],
                                                                                                 [[15, 24], 0.3]],
                                                               priority_distribution=[[[0, 3], 1]],
                                                               drop_points_distribution=drop_points_distribution,
                                                               azimuth_distribution=[[[0, 359], 1]],
                                                               elevation_distribution=[[[90, 90], 0.5],
                                                                                       [[30, 89], 0.5]],
                                                               package_distribution=[[PackageType.TINY.name, 0.5],
                                                                                     [PackageType.SMALL.name, 0.3],
                                                                                     [PackageType.MEDIUM.name, 0.2],
                                                                                     [PackageType.LARGE.name, 0]],
                                                               random_seed=10)

        self.assertEqual(delivery_request_dict1, delivery_request_dict2)

    def test_create_delivery_requests_without_seed(self):
        delivery_request_dict1 = create_delivery_requests_dict(num_of_delivery_requests_range=[5, 5],
                                                               num_of_delivery_options_distribution=[[[1, 2], 1]],
                                                               num_of_customer_deliveries_distribution=[[[1, 3], 0.9],
                                                                                                        [[4, 5], 0.1]],
                                                               num_of_package_delivery_plans_distribution=[
                                                                   [[1, 3], 0.7], [[4, 5], 0.3]],
                                                               main_time_window_length_range=[24, 24],
                                                               time_windows_length_distribution=[[[1, 2], 0.1],
                                                                                                 [[3, 5], 0.3],
                                                                                                 [[5, 15], 0.3],
                                                                                                 [[15, 24], 0.3]],
                                                               priority_distribution=[[[0, 3], 1]],
                                                               drop_points_distribution=[[[[0, 100], [0, 100]], 0.7],
                                                                                         [[[100, 200], [0, 100]], 0.3]],
                                                               azimuth_distribution=[[[0, 359], 1]],
                                                               elevation_distribution=[[[90, 90], 0.5],
                                                                                       [[30, 89], 0.5]],
                                                               package_distribution=[[PackageType.TINY.name, 0.5],
                                                                                     [PackageType.SMALL.name, 0.3],
                                                                                     [PackageType.MEDIUM.name, 0.2],
                                                                                     [PackageType.LARGE.name, 0]])

        delivery_request_dict2 = create_delivery_requests_dict(num_of_delivery_requests_range=[5, 5],
                                                               num_of_delivery_options_distribution=[[[1, 2], 1]],
                                                               num_of_customer_deliveries_distribution=[[[1, 3], 0.9],
                                                                                                        [[4, 5], 0.1]],
                                                               num_of_package_delivery_plans_distribution=[
                                                                   [[1, 3], 0.7], [[4, 5], 0.3]],
                                                               main_time_window_length_range=[24, 24],
                                                               time_windows_length_distribution=[[[1, 2], 0.1],
                                                                                                 [[3, 5], 0.3],
                                                                                                 [[5, 15], 0.3],
                                                                                                 [[15, 24], 0.3]],
                                                               priority_distribution=[[[0, 3], 1]],
                                                               drop_points_distribution=[[[[0, 100], [0, 100]], 0.7],
                                                                                         [[[100, 200], [0, 100]], 0.3]],
                                                               azimuth_distribution=[[[0, 359], 1]],
                                                               elevation_distribution=[[[90, 90], 0.5],
                                                                                       [[30, 89], 0.5]],
                                                               package_distribution=[[PackageType.TINY.name, 0.5],
                                                                                     [PackageType.SMALL.name, 0.3],
                                                                                     [PackageType.MEDIUM.name, 0.2],
                                                                                     [PackageType.LARGE.name, 0]])
        self.assertNotEqual(delivery_request_dict1, delivery_request_dict2)

    def test_create_delivery_requests_json(self):
        create_delivery_requests_json('TempDelReqTest.json', num_of_delivery_requests_range=[5, 5],
                                      num_of_delivery_options_distribution=[[[1, 2], 1]],
                                      num_of_customer_deliveries_distribution=[[[1, 3], 0.9], [[4, 5], 0.1]],
                                      num_of_package_delivery_plans_distribution=[[[1, 3], 0.7], [[4, 5], 0.3]],
                                      main_time_window_length_range=[24, 24],
                                      time_windows_length_distribution=[[[1, 2], 0.1], [[3, 5], 0.3],
                                                                        [[5, 15], 0.3],
                                                                        [[15, 24], 0.3]],
                                      priority_distribution=[[[0, 3], 1]],
                                      drop_points_distribution=[[[[0, 100], [0, 100]], 0.7],
                                                                [[[100, 200], [0, 100]], 0.3]],
                                      azimuth_distribution=[[[0, 359], 1]],
                                      elevation_distribution=[[[90, 90], 0.5], [[30, 89], 0.5]],
                                      package_distribution=[[PackageType.TINY.name, 0.5],
                                                            [PackageType.SMALL.name, 0.3],
                                                            [PackageType.MEDIUM.name, 0.2],
                                                            [PackageType.LARGE.name, 0]])
        dr = create_delivery_requests_from_file('TempDelReqTest.json')
        self.assertEqual(len(dr), 5)
