import string
from dataclasses import dataclass
from random import Random
from typing import List

import params
from common.entities.package import PackageType
from common.utils import json_file_handler


@dataclass
class IntRange:
    start: int
    stop: int


@dataclass
class WeightedIntRange:
    start: int
    stop: int
    weight: float


@dataclass
class FloatRange:
    start: float
    stop: float


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


class PackageDistribution:
    def __init__(self, weighted_packages: [(PackageType, float)]):
        self._packages, self._weights = zip(*weighted_packages)

    @property
    def packages(self) -> List[PackageType]:
        return self._packages

    @property
    def weights(self) -> List[float]:
        return self._weights


def create_delivery_requests_json(file_path: string,
                                  num_of_delivery_requests_range: IntRange,
                                  num_of_delivery_options_distribution: IntDistribution,
                                  num_of_customer_deliveries_distribution: [[]],
                                  num_of_package_delivery_plans_distribution: [[]],
                                  main_time_window_length_range: IntRange,
                                  time_windows_length_distribution: [[]],
                                  priority_distribution: [[]],
                                  drop_points_distribution: PointDistribution,
                                  azimuth_distribution: [[]],
                                  elevation_distribution: [[]],
                                  package_distribution: PackageDistribution,
                                  random_seed=None):
    """
    input explanations :
    any input as range : [a,b] :[int, int]
    generates random number in range [a,b] using uniform distribution

    any input as distribution : [[[a,b],p1],[[c,d],p2]],...] : [[[int , int], float],...]]
    generates random number with probability p1 to be in range [a,b] and probability p2 to be in range [c,d]

    drop_points_distribution : [[[[a,b],[c,d]],p1],...] : [[[[int, int],[int, int]], float],...]
    generates 2 random numbers (x,y) with probability p1 to be in range [a,b] for x and [c,d] for y...

    package_distribution : [[PackageType name, p1],...] : [[string, float] ,..]
    generates package type with probability p1

    """

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
                                  num_of_customer_deliveries_distribution: [[]],
                                  num_of_package_delivery_plans_distribution: [[]],
                                  main_time_window_length_range,
                                  time_windows_length_distribution: [[]],
                                  priority_distribution: [[]],
                                  drop_points_distribution: PointDistribution,
                                  azimuth_distribution: [[]],
                                  elevation_distribution: [[]],
                                  package_distribution: PackageDistribution,
                                  random_seed: int = None) -> dict:
    """
    input explanations :
    any input as range : [a,b] :[int, int]
    generates random number in range [a,b] using uniform distribution

    any input as distribution : [[[a,b],p1],[[c,d],p2]],...] : [[[int , int], float],...]]
    generates random number with probability p1 to be in range [a,b] and probability p2 to be in range [c,d]

    drop_points_distribution : [[[[a,b],[c,d]],p1],...] : [[[[int, int],[int, int]], float],...]
    generates 2 random numbers (x,y) with probability p1 to be in range [a,b] for x and [c,d] for y...

    package_distribution : [[PackageType name, p1],...] : [[string, float] ,..]
    generates package type with probability p1

    """

    rand = Random()
    if random_seed:
        rand.seed(random_seed)

    num_of_delivery_requests = rand.randint(num_of_delivery_requests_range.start,
                                            num_of_delivery_requests_range.stop)
    num_of_delivery_options = rand.choices(num_of_delivery_options_distribution.population,
                                           num_of_delivery_options_distribution.weights)[0]
    num_of_customer_deliveries = rand.choices(*get_distribution(num_of_customer_deliveries_distribution))[0]
    num_of_package_delivery_plans = rand.choices(*get_distribution(num_of_package_delivery_plans_distribution))[0]

    delivery_requests = []
    for _ in range(num_of_delivery_requests):
        delivery_requests.append(create_delivery_request_dict(azimuth_distribution, drop_points_distribution,
                                                              elevation_distribution, main_time_window_length_range,
                                                              num_of_customer_deliveries,
                                                              num_of_delivery_options, num_of_package_delivery_plans,
                                                              package_distribution,
                                                              priority_distribution, rand,
                                                              time_windows_length_distribution))

    return dict(delivery_requests=delivery_requests)


def create_delivery_request_dict(azimuth_distribution, drop_points_distribution,
                                 elevation_distribution, main_time_window_length_range, num_of_customer_deliveries,
                                 num_of_delivery_options, num_of_package_delivery_plans, package_distribution,
                                 priority_distribution, rand, time_windows_length_distribution) -> dict:
    time_window = get_time_window(main_time_window_length_range, time_windows_length_distribution, rand)
    priority = get_random_value_from_distribution(priority_distribution, rand)
    delivery_options = []
    delivery_request_dict = dict(delivery_options=delivery_options, time_window=time_window, priority=priority)
    for _ in range(num_of_delivery_options):
        delivery_options.append(__create_delivery_option_dict(azimuth_distribution, drop_points_distribution,
                                                              elevation_distribution, num_of_customer_deliveries,
                                                              num_of_package_delivery_plans,
                                                              package_distribution, rand))

    return delivery_request_dict


def __create_delivery_option_dict(azimuth_distribution, drop_points_distribution,
                                  elevation_distribution, num_of_customer_deliveries, num_of_package_delivery_plans,
                                  package_distribution, rand) -> dict:
    customer_deliveries = []
    delivery_option = dict(customer_deliveries=customer_deliveries)
    for _ in range(num_of_customer_deliveries):
        customer_deliveries.append(__create_customer_delivery_dict(azimuth_distribution, drop_points_distribution,
                                                                   elevation_distribution,
                                                                   num_of_package_delivery_plans,
                                                                   package_distribution, rand))
    return delivery_option


def __create_customer_delivery_dict(azimuth_distribution, drop_points_distribution,
                                    elevation_distribution, num_of_package_delivery_plans,
                                    package_distribution, rand) -> dict:
    package_delivery_plans = []
    customer_delivery = dict(package_delivery_plans=package_delivery_plans)
    for _ in range(num_of_package_delivery_plans):
        package_delivery_plans.append(
            __create_package_delivery_plan_dict(azimuth_distribution, drop_points_distribution,
                                                elevation_distribution,
                                                package_distribution, rand))
    return customer_delivery


def __create_package_delivery_plan_dict(azimuth_distribution, drop_points_distribution, elevation_distribution,
                                        package_distribution, rand) -> dict:
    package_type = rand.choices(package_distribution.packages, package_distribution.weights)[0]

    drop_point_dict = __create_drop_point_dict(drop_points_distribution, rand)
    azimuth = get_random_value_from_distribution(azimuth_distribution, rand)
    elevation = get_random_value_from_distribution(elevation_distribution, rand)
    package_delivery_plan_dict = dict(package_type=package_type, azimuth=azimuth, elevation=elevation)
    package_delivery_plan_dict.update(drop_point_dict)
    return package_delivery_plan_dict


def __create_drop_point_dict(drop_points_distribution: PointDistribution, rand) -> dict:
    drop_point_area = rand.choices(drop_points_distribution.areas, drop_points_distribution.weights)[0]
    drop_point_x = rand.uniform(drop_point_area.x_range.start, drop_point_area.x_range.stop)
    drop_point_y = rand.uniform(drop_point_area.y_range.start, drop_point_area.y_range.stop)
    return dict(drop_point_x=drop_point_x, drop_point_y=drop_point_y)


def get_random_value_from_distribution(distribution, rand):
    return rand.choices(*get_distribution(distribution))[0]


def get_distribution(distribution: [[]]) -> ([], []):
    population = []
    weights = []
    for range_prob in distribution:
        if isinstance(range_prob[0], list):
            values_range = list(range(*range_prob[0]))
            values_range.append(range_prob[0][1])
            prob = [range_prob[1] / len(values_range) for _ in values_range]
            population.extend(values_range)
            weights.extend(prob)
        else:
            population.append(range_prob[0])
            weights.append(range_prob[1])
    return population, weights


def get_time_window(main_time_window_length_range: [int], time_windows_length_distribution: [[]],
                    rand: Random) -> dict:
    """
    Assuming main_time_window_length isn't more than a month
    """

    main_time_window_length = rand.randint(*main_time_window_length_range)
    time_window_length = get_random_value_from_distribution(time_windows_length_distribution, rand)

    start_time = rand.randint(0, main_time_window_length - time_window_length)
    end_time = start_time + time_window_length
    return dict(
        start_time=dict(year=params.BASE_YEAR, month=params.BASE_MONTH, day=params.BASE_DAY + int(start_time / 24),
                        hour=start_time % 24, minute=params.BASE_MINUTE, second=params.BASE_SECOND),
        end_time=dict(year=params.BASE_YEAR, month=params.BASE_MONTH, day=params.BASE_DAY + int(end_time / 24),
                      hour=end_time % 24, minute=params.BASE_MINUTE, second=params.BASE_SECOND))
