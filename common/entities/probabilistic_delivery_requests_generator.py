import string
from random import Random

import params
from common.utils import json_file_handler


def create_delivery_requests_json(file_path: string,
                                  num_of_delivery_requests_range: [int],
                                  num_of_delivery_options_distribution: [[]],
                                  num_of_customer_deliveries_distribution: [[]],
                                  num_of_package_delivery_plans_distribution: [[]],
                                  main_time_window_length_range,
                                  time_windows_length_distribution: [[]],
                                  priority_distribution: [[]],
                                  drop_points_distribution: [[]],
                                  azimuth_distribution: [[]],
                                  elevation_distribution: [[]],
                                  package_distribution: [[]],
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
    json_file_handler.to_file(file_path, delivery_requests_dict)


def create_delivery_requests_dict(num_of_delivery_requests_range,
                                  num_of_delivery_options_distribution: [[]],
                                  num_of_customer_deliveries_distribution: [[]],
                                  num_of_package_delivery_plans_distribution: [[]],
                                  main_time_window_length_range,
                                  time_windows_length_distribution: [[]],
                                  priority_distribution: [[]],
                                  drop_points_distribution: [[]],
                                  azimuth_distribution: [[]],
                                  elevation_distribution: [[]],
                                  package_distribution: [[]],
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

    num_of_delivery_requests = rand.randint(*num_of_delivery_requests_range)
    num_of_delivery_options = rand.choices(*get_distribution(num_of_delivery_options_distribution))[0]
    num_of_customer_deliveries = rand.choices(*get_distribution(num_of_customer_deliveries_distribution))[0]
    num_of_package_delivery_plans = rand.choices(*get_distribution(num_of_package_delivery_plans_distribution))[0]

    delivery_requests = []
    for delivery_request_ind in range(num_of_delivery_requests):
        time_window = get_time_window(main_time_window_length_range, time_windows_length_distribution, rand)
        priority = rand.choices(*get_distribution(priority_distribution))[0]
        delivery_options = []
        delivery_requests.append(dict(delivery_options=delivery_options, time_window=time_window, priority=priority))
        for delivery_option_ind in range(num_of_delivery_options):
            customer_deliveries = []
            delivery_options.append(dict(customer_deliveries=customer_deliveries))
            for customer_delivery_ind in range(num_of_customer_deliveries):
                package_delivery_plans = []
                customer_deliveries.append(dict(package_delivery_plans=package_delivery_plans))
                for package_delivery_plan_ind in range(num_of_package_delivery_plans):
                    package_type = rand.choices(*get_distribution(package_distribution))[0]
                    drop_point_area = rand.choices(range(len(drop_points_distribution)),
                                                   [distribution[1] for distribution in drop_points_distribution])[0]
                    drop_points_range = drop_points_distribution[drop_point_area][0]
                    drop_point_x = rand.randint(*drop_points_range[0])
                    drop_point_y = rand.randint(*drop_points_range[1])
                    azimuth = rand.choices(*get_distribution(azimuth_distribution))[0]
                    elevation = rand.choices(*get_distribution(elevation_distribution))[0]
                    package_delivery_plans.append(
                        dict(package_type=package_type, drop_point_x=drop_point_x, drop_point_y=drop_point_y,
                             azimuth=azimuth, elevation=elevation))

    return dict(delivery_requests=delivery_requests)


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
    time_window_length = rand.choices(*get_distribution(time_windows_length_distribution))[0]

    start_time = rand.randint(0, main_time_window_length - time_window_length)
    end_time = start_time + time_window_length
    return dict(
        start_time=dict(year=params.BASE_YEAR, month=params.BASE_MONTH, day=params.BASE_DAY + int(start_time / 24),
                        hour=start_time % 24, minute=params.BASE_MINUTE, second=params.BASE_SECOND),
        end_time=dict(year=params.BASE_YEAR, month=params.BASE_MONTH, day=params.BASE_DAY + int(end_time / 24),
                      hour=end_time % 24, minute=params.BASE_MINUTE, second=params.BASE_SECOND))
