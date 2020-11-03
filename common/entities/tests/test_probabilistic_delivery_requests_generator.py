import unittest
from datetime import datetime
from pathlib import Path
from random import Random

from time_window import TimeWindow
import params
from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.probabilistic_delivery_requests_generator import IntRange, IntDistribution, WeightedIntRange, \
    WeightedPointRange, PointDistribution, FloatRange, PackageDistribution, create_delivery_requests_dict, \
    create_delivery_requests_json, get_time_window
from geometry.geo_factory import create_point_2d
from input.delivery_requests_json_converter import create_delivery_requests_from_file
from common.math.angle import Angle, AngleUnit


class ProbabilisticDeliveryRequestsGenerationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rand = Random()
        cls.num_of_delivery_requests_range = IntRange(5, 5)
        cls.num_of_delivery_options_distribution = IntDistribution([WeightedIntRange(1, 2, 1)])
        cls.num_of_customer_deliveries_distribution = IntDistribution([WeightedIntRange(1, 3, 0.9),
                                                                       WeightedIntRange(4, 5, 0.1)])
        cls.num_of_package_delivery_plans_distribution = IntDistribution([WeightedIntRange(1, 3, 0.7),
                                                                          WeightedIntRange(4, 5, 0.3)])
        cls.main_time_window_length_range = IntRange(24, 24)
        cls.time_windows_length_distribution = IntDistribution([WeightedIntRange(1, 2, 0.1),
                                                                WeightedIntRange(3, 5, 0.3),
                                                                WeightedIntRange(5, 15, 0.3),
                                                                WeightedIntRange(15, 24, 0.3)])
        cls.priority_distribution = IntDistribution([WeightedIntRange(0, 3, 1)])
        cls.drop_points_distribution = PointDistribution([WeightedPointRange(FloatRange(0.0, 100.0),
                                                                             FloatRange(0.0, 100.0), 0.7),
                                                          WeightedPointRange(FloatRange(100.0, 200.0),
                                                                             FloatRange(0.0, 100.0), 0.3)])
        cls.azimuth_distribution = IntDistribution([WeightedIntRange(0, 359, 1)])
        cls.elevation_distribution = IntDistribution([WeightedIntRange(90, 90, 0.5),
                                                      WeightedIntRange(30, 89, 0.5)])
        cls.package_distribution = PackageDistribution([(PackageType.TINY.name, 0.5),
                                                        (PackageType.SMALL.name, 0.3),
                                                        (PackageType.MEDIUM.name, 0.2),
                                                        (PackageType.LARGE.name, 0)])
        cls.random_seed = 10
        cls.output_json_path = Path('TempDelReqTest.json')

    def test_int_distribution(self):
        distribution = IntDistribution([WeightedIntRange(0, 359, 1)])
        self.assertEqual(len(distribution.population), 360)
        self.assertEqual(distribution.weights[0], 1 / 360)
        self.assertAlmostEqual(sum(distribution.weights), 1)

    def test_package_distribution(self):
        distribution = PackageDistribution([(PackageType.TINY.name, 0.5),
                                            (PackageType.SMALL.name, 0.3),
                                            (PackageType.MEDIUM.name, 0.2),
                                            (PackageType.LARGE.name, 0)])
        self.assertEqual(len(distribution.packages), 4)
        self.assertEqual(distribution.weights[0], 0.5)

    def test_get_time_window_one_day_3_hours(self):
        time_window = get_time_window(IntRange(24, 24), IntDistribution([WeightedIntRange(1, 2, 0),
                                                                         WeightedIntRange(3, 3, 1)]), self.rand)
        self.assertGreater(time_window['end_time']['hour'], time_window['start_time']['hour'])
        self.assertEqual(time_window['end_time']['hour'] - time_window['start_time']['hour'], 3)
        self.assertLessEqual(int(time_window['end_time']['hour']), 24)
        self.assertEqual(time_window['end_time']['day'] - time_window['start_time']['day'], 0)
        self.assertEqual(time_window['start_time']['day'], params.BASE_DAY)

    def test_get_time_window_two_days_28_hours(self):
        time_window = get_time_window(IntRange(48, 48), IntDistribution([WeightedIntRange(28, 28, 1)]), self.rand)
        self.assertGreater(time_window['end_time']['day'], time_window['start_time']['day'])
        self.assertEqual(time_window['end_time']['hour'] - time_window['start_time']['hour'] + 24, 28)
        self.assertLessEqual(time_window['end_time']['hour'], 24)
        self.assertEqual(time_window['start_time']['day'], params.BASE_DAY)
        self.assertEqual(time_window['end_time']['day'], params.BASE_DAY + 1)

    def test_create_delivery_options_dict(self):
        num_of_delivery_requests_range = IntRange(100, 100)
        num_of_delivery_options_distribution = IntDistribution([WeightedIntRange(1, 100, 1)])

        delivery_request_dict1 = create_delivery_requests_dict(
            num_of_delivery_requests_range=num_of_delivery_requests_range,
            num_of_delivery_options_distribution=num_of_delivery_options_distribution,
            num_of_customer_deliveries_distribution=self.num_of_customer_deliveries_distribution,
            num_of_package_delivery_plans_distribution=self.num_of_package_delivery_plans_distribution,
            main_time_window_length_range=self.main_time_window_length_range,
            time_windows_length_distribution=self.time_windows_length_distribution,
            priority_distribution=self.priority_distribution,
            drop_points_distribution=self.drop_points_distribution,
            azimuth_distribution=self.azimuth_distribution,
            elevation_distribution=self.elevation_distribution,
            package_distribution=self.package_distribution,
            random_seed=self.random_seed)

        delivery_options_size_list = [len(delivery_request["delivery_options"])
                                      for delivery_request in delivery_request_dict1["delivery_requests"]]
        self.assertGreater(len(delivery_options_size_list), len(set(delivery_options_size_list)))
        self.assertGreater(len(set(delivery_options_size_list)), 1)

    def test_create_delivery_requests_dict_with_seed(self):
        delivery_request_dict1 = create_delivery_requests_dict(
            num_of_delivery_requests_range=self.num_of_delivery_requests_range,
            num_of_delivery_options_distribution=self.num_of_delivery_options_distribution,
            num_of_customer_deliveries_distribution=self.num_of_customer_deliveries_distribution,
            num_of_package_delivery_plans_distribution=self.num_of_package_delivery_plans_distribution,
            main_time_window_length_range=self.main_time_window_length_range,
            time_windows_length_distribution=self.time_windows_length_distribution,
            priority_distribution=self.priority_distribution,
            drop_points_distribution=self.drop_points_distribution,
            azimuth_distribution=self.azimuth_distribution,
            elevation_distribution=self.elevation_distribution,
            package_distribution=self.package_distribution,
            random_seed=self.random_seed)
        delivery_request_dict2 = create_delivery_requests_dict(
            num_of_delivery_requests_range=self.num_of_delivery_requests_range,
            num_of_delivery_options_distribution=self.num_of_delivery_options_distribution,
            num_of_customer_deliveries_distribution=self.num_of_customer_deliveries_distribution,
            num_of_package_delivery_plans_distribution=self.num_of_package_delivery_plans_distribution,
            main_time_window_length_range=self.main_time_window_length_range,
            time_windows_length_distribution=self.time_windows_length_distribution,
            priority_distribution=self.priority_distribution,
            drop_points_distribution=self.drop_points_distribution,
            azimuth_distribution=self.azimuth_distribution,
            elevation_distribution=self.elevation_distribution,
            package_distribution=self.package_distribution,
            random_seed=self.random_seed)

        self.assertEqual(delivery_request_dict1, delivery_request_dict2)

    def test_create_delivery_requests__dict_without_seed(self):
        delivery_request_dict1 = create_delivery_requests_dict(
            num_of_delivery_requests_range=self.num_of_delivery_requests_range,
            num_of_delivery_options_distribution=self.num_of_delivery_options_distribution,
            num_of_customer_deliveries_distribution=self.num_of_customer_deliveries_distribution,
            num_of_package_delivery_plans_distribution=self.num_of_package_delivery_plans_distribution,
            main_time_window_length_range=self.main_time_window_length_range,
            time_windows_length_distribution=self.time_windows_length_distribution,
            priority_distribution=self.priority_distribution,
            drop_points_distribution=self.drop_points_distribution,
            azimuth_distribution=self.azimuth_distribution,
            elevation_distribution=self.elevation_distribution,
            package_distribution=self.package_distribution)
        delivery_request_dict2 = create_delivery_requests_dict(
            num_of_delivery_requests_range=self.num_of_delivery_requests_range,
            num_of_delivery_options_distribution=self.num_of_delivery_options_distribution,
            num_of_customer_deliveries_distribution=self.num_of_customer_deliveries_distribution,
            num_of_package_delivery_plans_distribution=self.num_of_package_delivery_plans_distribution,
            main_time_window_length_range=self.main_time_window_length_range,
            time_windows_length_distribution=self.time_windows_length_distribution,
            priority_distribution=self.priority_distribution,
            drop_points_distribution=self.drop_points_distribution,
            azimuth_distribution=self.azimuth_distribution,
            elevation_distribution=self.elevation_distribution,
            package_distribution=self.package_distribution)

        self.assertNotEqual(delivery_request_dict1, delivery_request_dict2)

    def test_create_delivery_request_from_json(self):
        expected_request = DeliveryRequest(
            delivery_options=[
                DeliveryOption([
                    CustomerDelivery([
                        PackageDeliveryPlan(drop_point=create_point_2d(5.0, 7.0),
                                            azimuth=Angle(45, AngleUnit.DEGREE),
                                            elevation=Angle(30, AngleUnit.DEGREE),
                                            package_type=PackageType.MEDIUM)])])],
            time_window=TimeWindow(
                datetime(params.BASE_YEAR, params.BASE_MONTH, params.BASE_DAY,
                         params.BASE_HOUR, params.BASE_MINUTE, params.BASE_SECOND),
                datetime(params.BASE_YEAR, params.BASE_MONTH, params.BASE_DAY,
                         params.BASE_HOUR + 2, params.BASE_MINUTE, params.BASE_SECOND)),
            priority=0)

        create_delivery_requests_json(
            self.output_json_path,
            num_of_delivery_requests_range=IntRange(1, 1),
            num_of_delivery_options_distribution=IntDistribution([WeightedIntRange(1, 1, 1)]),
            num_of_customer_deliveries_distribution=IntDistribution([WeightedIntRange(1, 1, 1)]),
            num_of_package_delivery_plans_distribution=IntDistribution([WeightedIntRange(1, 1, 1)]),
            main_time_window_length_range=IntRange(2, 2),
            time_windows_length_distribution=IntDistribution([WeightedIntRange(2, 2, 1)]),
            priority_distribution=IntDistribution([WeightedIntRange(0, 0, 1)]),
            drop_points_distribution=PointDistribution([WeightedPointRange(FloatRange(5.0, 5.0),
                                                                           FloatRange(7.0, 7.0), 1)]),
            azimuth_distribution=IntDistribution([WeightedIntRange(45, 45, 1)]),
            elevation_distribution=IntDistribution([WeightedIntRange(30, 30, 1)]),
            package_distribution=PackageDistribution([(PackageType.MEDIUM.name, 1)]))
        request_from_json = create_delivery_requests_from_file(self.output_json_path)

        self.assertEqual(len(request_from_json), 1)
        self.assertEqual(request_from_json[0], expected_request)

    def test_create_Multiple_delivery_requests_from_json(self):
        create_delivery_requests_json(
            self.output_json_path,
            num_of_delivery_requests_range=self.num_of_delivery_requests_range,
            num_of_delivery_options_distribution=self.num_of_delivery_options_distribution,
            num_of_customer_deliveries_distribution=self.num_of_customer_deliveries_distribution,
            num_of_package_delivery_plans_distribution=self.num_of_package_delivery_plans_distribution,
            main_time_window_length_range=self.main_time_window_length_range,
            time_windows_length_distribution=self.time_windows_length_distribution,
            priority_distribution=self.priority_distribution,
            drop_points_distribution=self.drop_points_distribution,
            azimuth_distribution=self.azimuth_distribution,
            elevation_distribution=self.elevation_distribution,
            package_distribution=self.package_distribution)
        dr = create_delivery_requests_from_file(self.output_json_path)

        self.assertEqual(len(dr), 5)
