import unittest
from datetime import time, date, timedelta
from pathlib import Path
from pprint import pprint
from random import Random
from typing import List
from common.entities.drone_formation import FormationSize
import numpy as np
from common.entities.delivery_request import build_delivery_request_distribution, \
    DeliveryRequest, PriorityDistribution
from common.entities.drone_loading_dock import DroneLoadingDockDistribution
from common.entities.drone_loading_station import DroneLoadingStationDistribution
from common.entities.package import PackageDistribution, PackageType
from common.entities.temporal import DateTimeExtension, TimeWindowDistribution, TimeDeltaDistribution, \
    TimeDeltaExtension, DateTimeDistribution
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from common.tools.empty_drone_delivery_board_generation import build_empty_drone_delivery_board
from common.tools.fleet_property_sets import *
from end_to_end.minimum_end_to_end import MinimumEnd2EndConfig, DataLoader, MinimumEnd2End
from end_to_end.scenario import ScenarioDistribution
from geometry.geo_distribution import NormalPointDistribution, UniformPointInBboxDistribution
from geometry.geo_factory import create_point_2d
from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.basic.pltgantt_drawer import create_gantt_drawer
from visualization.operational import operational_drawer2d
from visualization.operational import operational_gantt_drawer

# west_lon = 34.8288611
# east_lon = 35.9786527
# south_lat = 32.3508222
# north_lat = 33.3579972
west_lon = 34.83927
east_lon = 35.32341
south_lat = 31.77279
north_lat = 32.19276

ZERO_TIME = DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(0, 0, 0))

def create_standad_full_day_test_time():
    default_start = ZERO_TIME
    default_time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=23, minutes=59))])
    default_dt_options = [default_start]
    return TimeWindowDistribution(DateTimeDistribution(default_dt_options), default_time_delta_distrib)



def _create_delivery_request_distribution():
    package_distribution = create_single_package_distribution()
    zero_time = ZERO_TIME
    time_delta_distrib = TimeDeltaDistribution([TimeDeltaExtension(timedelta(hours=3, minutes=0))])
    dt_options = [zero_time.add_time_delta(TimeDeltaExtension(timedelta(hours=x))) for x in range(24 - 3)]

    time_window_distribution = TimeWindowDistribution(DateTimeDistribution(dt_options), time_delta_distrib)

    delivery_request_distribution = build_delivery_request_distribution(
        package_type_distribution=package_distribution,
        relative_dr_location_distribution=NormalPointDistribution(create_point_2d(35.11,32.0), 0.03, 0.05),
        priority_distribution=PriorityDistribution(list(range(1, 10))),
        time_window_distribution=time_window_distribution)
    return delivery_request_distribution


def create_single_package_distribution():
    package_type_distribution_dict = {PackageType.LARGE.name: 1}
    package_distribution = PackageDistribution(package_distribution_dict=package_type_distribution_dict)
    return package_distribution


def _create_empty_drone_delivery_board(
        formation_size_policy: dict = {FormationSize.MINI: 1, FormationSize.MEDIUM: 0},
        configurations_policy: dict = {Configurations.LARGE_X2: 0.9,
                                       Configurations.MEDIUM_X4: 0.1,
                                       Configurations.SMALL_X8: 0,
                                       Configurations.TINY_X16: 0}
        , platform_type: PlatformType = PlatformType.platform_1,
        size: int = 30):
    formation_size_property_set = PlatformFormationsSizePolicyPropertySet(formation_size_policy)
    configuration_policy_property_set = PlatformConfigurationsPolicyPropertySet(configurations_policy)
    platform_property_set = PlatformPropertySet(platform_type=platform_type,
                                                configuration_policy=configuration_policy_property_set,
                                                formation_policy=formation_size_property_set,
                                                size=size)
    return build_empty_drone_delivery_board(platform_property_set)


class BasicMinimumEnd2EndPresentation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scenario_distribution = ScenarioDistribution(
            zero_time_distribution=DateTimeDistribution([ZERO_TIME]),
            delivery_requests_distribution=_create_delivery_request_distribution(),
            drone_loading_docks_distribution=
            DroneLoadingDockDistribution(drone_loading_station_distributions=
                                         DroneLoadingStationDistribution(drone_station_locations_distribution=
                                                                         UniformPointInBboxDistribution(west_lon,
                                                                                                        east_lon,
                                                                                                        south_lat,
                                                                                                        north_lat)),
                                         time_window_distributions=create_standad_full_day_test_time()))
        cls.matcher_config = Path("end_to_end/tests/jsons/test_matcher_config.json")

    def test_small_scenario(self):
        empty_drone_delivery_board = _create_empty_drone_delivery_board(size=20)
        minimum_end_to_end = MinimumEnd2End(
            scenario=self.scenario_distribution.choose_rand(random=Random(10), amount=37),
            empty_drone_delivery_board=empty_drone_delivery_board)
        fully_connected_graph = minimum_end_to_end.create_fully_connected_graph_model()
        # graph_exporter = OrtoolsGraphExporter()
        # travel_times = np.array(graph_exporter.export_travel_times(graph=fully_connected_graph))
        # time_windows = np.array(graph_exporter.export_time_windows(graph=fully_connected_graph,zero_time=minimum_end_to_end.zero_time))

        delivery_board = minimum_end_to_end.calc_assignment(fully_connected_graph, self.matcher_config)
        print(delivery_board)

        drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC)
        operational_drawer2d.add_delivery_board(drawer, delivery_board, draw_dropped=True)
        drawer.draw(False)

        row_names = ["Dropped Out"] + [delivery.drone_formation.get_package_type_volumes().get_package_types_volumes()
                                       for delivery in delivery_board.drone_deliveries]
        drawer = create_gantt_drawer(zero_time=DateTimeExtension.from_dt(fully_connected_graph.zero_time),
                                     hours_period=24,
                                     row_names=row_names,
                                     rows_title='Carried Package type: ' + str(PackageType.get_all_names())
                                     )
        operational_gantt_drawer.add_delivery_board(drawer, delivery_board, True)
        drawer.draw(True)

