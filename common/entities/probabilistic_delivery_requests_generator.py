# from __future__ import annotations
#
# import string
# from dataclasses import dataclass
# from random import Random
# from typing import List
#
# from common.entities.package import PackageType
# from common.utils import json_file_handler
# from geometry.geo2d import Point2D
# from geometry.geo_factory import create_point_2d
#
#
# @dataclass
# class IntRange:
#     start: int
#     stop: int
#
#     def calc_rand_in_range(self, random_generator) -> int:
#         return random_generator.randint(self.start, self.stop)
#
#
# @dataclass
# class WeightedIntRange:
#     start: int
#     stop: int
#     weight: float
#
#
# @dataclass
# class FloatRange:
#     start: float
#     stop: float
#
#     def calc_rand_in_range(self, random_generator) -> float:
#         return random_generator.uniform(self.start, self.stop)
#
#
# @dataclass
# class WeightedFloatRange:
#     start: float
#     stop: float
#     weight: float
#
#     def calc_rand_in_range(self, random_generator) -> float:
#         return random_generator.uniform(self.start, self.stop)
#
#
# @dataclass
# class WeightedPointRange:
#     x_range: FloatRange
#     y_range: FloatRange
#     weight: float
#
#     def calc_point_in_range(self, random_generator) -> Point2D:
#         return create_point_2d(self.x_range.calc_rand_in_range(random_generator),
#                                self.y_range.calc_rand_in_range(random_generator))
#
#
# class IntDistribution:
#     def __init__(self, ranges: [WeightedIntRange]):
#         self._population = []
#         self._weights = []
#         for range_ in ranges:
#             values = list(range(range_.start, range_.stop))
#             values.append(range_.stop)
#             relative_weights = [range_.weight / len(values) for _ in values]
#             self._population.extend(values)
#             self._weights.extend(relative_weights)
#
#     @property
#     def population(self) -> List[int]:
#         return self._population
#
#     @property
#     def weights(self) -> List[float]:
#         return self._weights
#
#     def calc_rand_in_range(self, random_generator) -> int:
#         return random_generator.choices(self.population, self.weights)[0]
#
#
# class PointDistribution:
#     def __init__(self, ranges: [WeightedPointRange]):
#         self._areas = ranges
#         self._weights = [range_.weight for range_ in ranges]
#
#     @property
#     def areas(self) -> List[WeightedPointRange]:
#         return self._areas
#
#     @property
#     def weights(self) -> List[float]:
#         return self._weights
#
#     def calc_rand_in_range(self, random_generator) -> Point2D:
#         drop_point_area = random_generator.choices(self.areas, self.weights)[0]
#         drop_point_x = drop_point_area.x_range.calc_rand_in_range(random_generator)
#         drop_point_y = drop_point_area.y_range.calc_rand_in_range(random_generator)
#         return create_point_2d(drop_point_x, drop_point_y)
#
#
#
#
#
# # @dataclass
# # class PackageDeliveryPlanDistribution:
# #     azimuth_distribution: IntDistribution = IntDistribution([WeightedIntRange(0, 360, 1)])
# #     drop_points_distribution: PointDistribution = PointDistribution([
# #         WeightedPointRange(FloatRange(0, 100), FloatRange(0, 100), 1)])
# #     elevation_distribution: IntDistribution = IntDistribution([WeightedIntRange(0, 0, 1)])
# #     package_distribution: PackageDistribution = PackageDistribution([(PackageType.MEDIUM, 1)])
#
#
# def create_delivery_requests_json(file_path: string,
#                                   num_of_delivery_requests_range: IntRange,
#                                   num_of_delivery_options_distribution: IntDistribution,
#                                   num_of_customer_deliveries_distribution: IntDistribution,
#                                   num_of_package_delivery_plans_distribution: IntDistribution,
#                                   main_time_window_length_range: IntRange,
#                                   time_windows_length_distribution: IntDistribution,
#                                   priority_distribution: IntDistribution,
#                                   drop_points_distribution: PointDistribution,
#                                   azimuth_distribution: IntDistribution,
#                                   elevation_distribution: IntDistribution,
#                                   package_distribution: PackageDistribution,
#                                   random_seed=None):
#     delivery_requests_dict = create_delivery_requests_dict(num_of_delivery_requests_range,
#                                                            num_of_delivery_options_distribution,
#                                                            num_of_customer_deliveries_distribution,
#                                                            num_of_package_delivery_plans_distribution,
#                                                            main_time_window_length_range,
#                                                            time_windows_length_distribution,
#                                                            priority_distribution,
#                                                            drop_points_distribution,
#                                                            azimuth_distribution,
#                                                            elevation_distribution,
#                                                            package_distribution,
#                                                            random_seed)
#
#     json_file_handler.create_json_from_dict(file_path, delivery_requests_dict)
#
#
# def create_delivery_requests_dict(num_of_delivery_requests_range: IntRange,
#                                   num_of_delivery_options_distribution: IntDistribution,
#                                   num_of_customer_deliveries_distribution: IntDistribution,
#                                   num_of_package_delivery_plans_distribution: IntDistribution,
#                                   main_time_window_length_range: IntRange,
#                                   time_windows_length_distribution: IntDistribution,
#                                   priority_distribution: IntDistribution,
#                                   package_delivery_plan_distribution: PackageDeliveryPlanDistribution,
#                                   random_seed: int = None) -> dict:
#     rand = Random(random_seed)
#
#     delivery_requests = []
#     for _ in range(num_of_delivery_requests_range.calc_rand_in_range(rand)):
#         # delivery_requests.append(create_delivery_request_dict(main_time_window_length_range,
#         #                                                       num_of_customer_deliveries_distribution,
#         #                                                       num_of_delivery_options_distribution,
#         #                                                       num_of_package_delivery_plans_distribution,
#         #                                                       priority_distribution,
#         #                                                       time_windows_length_distribution,
#         #                                                       package_delivery_plan_distribution: PackageDeliveryPlanDistribution,
#         # rand: Random))
#         return dict(delivery_requests=delivery_requests)
#
#     def create_delivery_request_dict(main_time_window_length_range,
#                                      num_of_customer_deliveries_distribution,
#                                      num_of_delivery_options_distribution,
#                                      num_of_package_delivery_plans_distribution,
#                                      priority_distribution,
#                                      time_windows_length_distribution,
#                                      package_delivery_plan_distribution: PackageDeliveryPlanDistribution,
#                                      rand: Random) -> dict:
#         time_window = PackageDistribution.get_time_window(main_time_window_length_range,
#                                                           time_windows_length_distribution,
#                                                           rand)
#         priority = priority_distribution.calc_rand_in_range(rand)
#         delivery_options = []
#         delivery_request_dict = dict(delivery_options=delivery_options, time_window=time_window, priority=priority)
#         for _ in range(num_of_delivery_options_distribution.calc_rand_in_range(rand)):
#             delivery_options.append(__create_delivery_option_dict(num_of_customer_deliveries_distribution,
#                                                                   num_of_package_delivery_plans_distribution,
#                                                                   package_delivery_plan_distribution,
#                                                                   rand))
#         return delivery_request_dict
#
#     def __create_delivery_option_dict(num_of_customer_deliveries_distribution: IntDistribution,
#                                       num_of_package_delivery_plans_distribution: IntDistribution,
#                                       package_delivery_plan_distribution: PackageDeliveryPlanDistribution,
#                                       rand: Random) -> dict:
#         customer_deliveries = []
#         delivery_option = dict(customer_deliveries=customer_deliveries)
#         for _ in range(num_of_customer_deliveries_distribution.calc_rand_in_range(rand)):
#             customer_deliveries.append(
#                 PackageDistribution.__create_customer_delivery_dict(num_of_package_delivery_plans_distribution,
#                                                                     package_delivery_plan_distribution, rand))
#             return delivery_option
#
#     def __create_customer_delivery_dict(num_of_package_delivery_plans_distribution: IntDistribution,
#                                         package_delivery_plan_distribution: PackageDeliveryPlanDistribution,
#                                         rand: Random) -> dict:
#         package_delivery_plans = []
#         customer_delivery = dict(package_delivery_plans=package_delivery_plans)
#         for _ in range(num_of_package_delivery_plans_distribution.calc_rand_in_range(rand)):
#             package_delivery_plans.append(__create_package_delivery_plan_dict(package_delivery_plan_distribution, rand))
#         return customer_delivery
#
#     def __create_package_delivery_plan_dict(pdp_distribution: PackageDeliveryPlanDistribution,
#                                             rand: Random) -> dict:
#         package_type = pdp_distribution.package_distribution.calc_rand_in_range(rand)
#         drop_point_dict = __create_drop_point_dict(pdp_distribution.drop_points_distribution, rand)
#         azimuth = pdp_distribution.azimuth_distribution.calc_rand_in_range(rand)
#         elevation = pdp_distribution.elevation_distribution.calc_rand_in_range(rand)
#         package_delivery_plan_dict = dict(package_type=package_type, azimuth=azimuth, elevation=elevation)
#         package_delivery_plan_dict.update(drop_point_dict)
#         return package_delivery_plan_dict
#
#     def __create_drop_point_dict(drop_points_distribution: PointDistribution, rand: Random) -> dict:
#         drop_point = drop_points_distribution.calc_rand_in_range(rand)
#         return dict(drop_point_x=drop_point.x, drop_point_y=drop_point.y)
#
