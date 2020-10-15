import string
from dataclasses import dataclass
from random import Random
from typing import List

import params
from common.entities.package import PackageType
from common.utils import json_file_handler
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d


@dataclass
class IntRange:
    start: int
    stop: int

    def random(self, random_generator) -> int:
        return random_generator.randint(self.start, self.stop)


@dataclass
class WeightedIntRange:
    start: int
    stop: int
    weight: float


@dataclass
class FloatRange:
    start: float
    stop: float

    def random(self, random_generator) -> float:
        return random_generator.uniform(self.start, self.stop)


@dataclass
class WeightedFloatRange:
    start: float
    stop: float
    weight: float


@dataclass
class WeightedPointRange:
    x_range: FloatRange
    y_range: FloatRange
    weight: float


class IntDistribution:
    def __init__(self, ranges: [WeightedIntRange]):
        self._population = []
        self._weights = []
        for range_ in ranges:
            values = list(range(range_.start, range_.stop))
            values.append(range_.stop)
            relative_weights = [range_.weight / len(values) for _ in values]
            self._population.extend(values)
            self._weights.extend(relative_weights)

    @property
    def population(self) -> List[int]:
        return self._population

    @property
    def weights(self) -> List[float]:
        return self._weights

    def random(self, random_generator) -> int:
        return random_generator.choices(self.population, self.weights)[0]


class PointDistribution:
    def __init__(self, ranges: [WeightedPointRange]):
        self._areas = ranges
        self._weights = [range_.weight for range_ in ranges]

    @property
    def areas(self) -> List[WeightedPointRange]:
        return self._areas

    @property
    def weights(self) -> List[float]:
        return self._weights

    def random(self, random_generator) -> Point2D:
        drop_point_area = random_generator.choices(self.areas, self.weights)[0]
        drop_point_x = drop_point_area.x_range.random(random_generator)
        drop_point_y = drop_point_area.y_range.random(random_generator)
        return create_point_2d(drop_point_x, drop_point_y)


class PackageDistribution:
    def __init__(self, weighted_packages: [(PackageType, float)]):
        self._packages, self._weights = zip(*weighted_packages)

    @property
    def packages(self) -> List[PackageType]:
        return self._packages

    @property
    def weights(self) -> List[float]:
        return self._weights

    def random(self, random_generator) -> PackageType:
        return random_generator.choices(self.packages, self.weights)[0]


def create_delivery_requests_json(file_path: string,
                                  num_of_delivery_requests_range: IntRange,
                                  num_of_delivery_options_distribution: IntDistribution,
                                  num_of_customer_deliveries_distribution: IntDistribution,
                                  num_of_package_delivery_plans_distribution: IntDistribution,
                                  main_time_window_length_range: IntRange,
                                  time_windows_length_distribution: IntDistribution,
                                  priority_distribution: IntDistribution,
                                  drop_points_distribution: PointDistribution,
                                  azimuth_distribution: IntDistribution,
                                  elevation_distribution: IntDistribution,
                                  package_distribution: PackageDistribution,
                                  random_seed=None):

    delivery_requests_dict = create_delivery_requests_dict(num_of_delivery_requests_range,
                                                           num_of_delivery_options_distribution,
                                                           num_of_customer_deliveries_distribution,
                                                           num_of_package_delivery_plans_distribution,
                                                           main_time_window_length_range,
                                                           time_windows_length_distribution,
                                                           priority_distribution,
                                                           drop_points_distribution,
                                                           azimuth_distribution,
                                                           elevation_distribution,
                                                           package_distribution,
                                                           random_seed)

    json_file_handler.create_json_from_dict(file_path, delivery_requests_dict)


def create_delivery_requests_dict(num_of_delivery_requests_range: IntRange,
                                  num_of_delivery_options_distribution: IntDistribution,
                                  num_of_customer_deliveries_distribution: IntDistribution,
                                  num_of_package_delivery_plans_distribution: IntDistribution,
                                  main_time_window_length_range: IntRange,
                                  time_windows_length_distribution: IntDistribution,
                                  priority_distribution: IntDistribution,
                                  drop_points_distribution: PointDistribution,
                                  azimuth_distribution: IntDistribution,
                                  elevation_distribution: IntDistribution,
                                  package_distribution: PackageDistribution,
                                  random_seed: int = None) -> dict:

    rand = Random(random_seed)

    delivery_requests = []
    for _ in range(num_of_delivery_requests_range.random(rand)):
        delivery_requests.append(create_delivery_request_dict(azimuth_distribution,
                                                              drop_points_distribution,
                                                              elevation_distribution,
                                                              main_time_window_length_range,
                                                              num_of_customer_deliveries_distribution,
                                                              num_of_delivery_options_distribution,
                                                              num_of_package_delivery_plans_distribution,
                                                              package_distribution,
                                                              priority_distribution,
                                                              rand,
                                                              time_windows_length_distribution))
    return dict(delivery_requests=delivery_requests)


def create_delivery_request_dict(azimuth_distribution,
                                 drop_points_distribution,
                                 elevation_distribution,
                                 main_time_window_length_range,
                                 num_of_customer_deliveries_distribution,
                                 num_of_delivery_options_distribution,
                                 num_of_package_delivery_plans_distribution,
                                 package_distribution,
                                 priority_distribution,
                                 rand,
                                 time_windows_length_distribution) -> dict:
    time_window = get_time_window(main_time_window_length_range, time_windows_length_distribution, rand)
    priority = priority_distribution.random(rand)
    delivery_options = []
    delivery_request_dict = dict(delivery_options=delivery_options, time_window=time_window, priority=priority)
    for _ in range(num_of_delivery_options_distribution.random(rand)):
        delivery_options.append(__create_delivery_option_dict(azimuth_distribution,
                                                              drop_points_distribution,
                                                              elevation_distribution,
                                                              num_of_customer_deliveries_distribution,
                                                              num_of_package_delivery_plans_distribution,
                                                              package_distribution,
                                                              rand))
    return delivery_request_dict


def __create_delivery_option_dict(azimuth_distribution,
                                  drop_points_distribution,
                                  elevation_distribution,
                                  num_of_customer_deliveries_distribution,
                                  num_of_package_delivery_plans_distribution,
                                  package_distribution,
                                  rand) -> dict:
    customer_deliveries = []
    delivery_option = dict(customer_deliveries=customer_deliveries)
    for _ in range(num_of_customer_deliveries_distribution.random(rand)):
        customer_deliveries.append(__create_customer_delivery_dict(azimuth_distribution,
                                                                   drop_points_distribution,
                                                                   elevation_distribution,
                                                                   num_of_package_delivery_plans_distribution,
                                                                   package_distribution,
                                                                   rand))
    return delivery_option


def __create_customer_delivery_dict(azimuth_distribution,
                                    drop_points_distribution,
                                    elevation_distribution,
                                    num_of_package_delivery_plans_distribution,
                                    package_distribution,
                                    rand) -> dict:
    package_delivery_plans = []
    customer_delivery = dict(package_delivery_plans=package_delivery_plans)
    for _ in range(num_of_package_delivery_plans_distribution.random(rand)):
        package_delivery_plans.append(
            __create_package_delivery_plan_dict(azimuth_distribution,
                                                drop_points_distribution,
                                                elevation_distribution,
                                                package_distribution,
                                                rand))
    return customer_delivery


def __create_package_delivery_plan_dict(azimuth_distribution,
                                        drop_points_distribution,
                                        elevation_distribution,
                                        package_distribution,
                                        rand) -> dict:
    package_type = package_distribution.random(rand)
    drop_point_dict = __create_drop_point_dict(drop_points_distribution, rand)
    azimuth = azimuth_distribution.random(rand)
    elevation = elevation_distribution.random(rand)
    package_delivery_plan_dict = dict(package_type=package_type, azimuth=azimuth, elevation=elevation)
    package_delivery_plan_dict.update(drop_point_dict)
    return package_delivery_plan_dict


def __create_drop_point_dict(drop_points_distribution: PointDistribution, rand) -> dict:
    drop_point = drop_points_distribution.random(rand)
    return dict(drop_point_x=drop_point.x, drop_point_y=drop_point.y)


def get_time_window(main_time_window_length_range: [int], time_windows_length_distribution: [[]],
                    rand: Random) -> dict:
    """
    Assuming main_time_window_length isn't more than a month
    """

    main_time_window_length = main_time_window_length_range.random(rand)
    time_window_length = time_windows_length_distribution.random(rand)

    start_time = IntRange(params.BASE_HOUR, main_time_window_length - time_window_length).random(rand)
    end_time = start_time + time_window_length
    return dict(
        start_time=dict(year=params.BASE_YEAR, month=params.BASE_MONTH, day=params.BASE_DAY + int(start_time / 24),
                        hour=start_time % 24, minute=params.BASE_MINUTE, second=params.BASE_SECOND),
        end_time=dict(year=params.BASE_YEAR, month=params.BASE_MONTH, day=params.BASE_DAY + int(end_time / 24),
                      hour=end_time % 24, minute=params.BASE_MINUTE, second=params.BASE_SECOND))
