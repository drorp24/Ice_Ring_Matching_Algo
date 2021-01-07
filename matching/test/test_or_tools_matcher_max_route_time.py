from datetime import datetime, timedelta
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PlatformType
from common.entities.base_entities.drone_delivery import EmptyDroneDelivery
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormations, FormationOptions, FormationSize
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import ExactTimeWindowDistribution
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeWindowExtension, DateTimeExtension, TimeDeltaExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from geometry.distribution.geo_distribution import ExactPointLocationDistribution
from geometry.geo_factory import create_point_2d
from matching.matcher_config import MatcherConfig, MatcherConfigProperties, MatcherSolver, MatcherConstraints, \
    CapacityConstraints, TimeConstraints, PriorityConstraints
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_matcher_constraints import MAX_OPERATION_TIME

ZERO_TIME = DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00))


class ORToolsMatcherMaxRouteTimeTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass
        cls.loading_dock = cls._create_loading_dock()

    def test_when_wait_time_longer_than_max_route_time(self):
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
                create_point_2d(0, 10)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=5)))),
                TimeWindowExtension(
                    since=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=400))),
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=500)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
        self.delivery_requests = dist.choose_rand(Random(42), amount={DeliveryRequest: 2})

        match_config = MatcherConfig(MatcherConfigProperties(
            zero_time=ZERO_TIME,
            first_solution_strategy="or_tools:path_cheapest_arc",
            solver=MatcherSolver(full_name="or_tools:automatic", timeout_sec=30),
            match_constraints=MatcherConstraints(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=500,
                                                 max_route_time=MAX_OPERATION_TIME,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            dropped_penalty=1000))

        self.graph = self._create_graph(self.delivery_requests, self.loading_dock)

        empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))
        empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_2))

        empty_board_1 = EmptyDroneDeliveryBoard([empty_drone_delivery_1])
        empty_board_2 = EmptyDroneDeliveryBoard([empty_drone_delivery_2])
        match_input_1 = MatcherInput(self.graph, empty_board_1, match_config)
        match_input_2 = MatcherInput(self.graph, empty_board_2, match_config)
        matcher_1 = ORToolsMatcher(match_input_1)
        matcher_2 = ORToolsMatcher(match_input_2)
        delivery_board_1 = matcher_1.match()
        delivery_board_2 = matcher_2.match()
        self.assertEqual(1, len(delivery_board_1.drone_deliveries[0].matched_requests))
        self.assertEqual(2, len(delivery_board_2.drone_deliveries[0].matched_requests))

    def test_when_travel_time_is_greater_than_max_route_time(self):
        # Assumption: calc_cost in graph_creator is time based on Euclidean distance between requests

        # Fleet definition:
        empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))
        edd1_max_range = empty_drone_delivery_1.drone_formation.get_formation_max_range_in_meters()
        edd1_max_endurance = empty_drone_delivery_1.drone_formation.max_route_times_in_minutes
        empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_2))
        edd2_max_range = empty_drone_delivery_2.drone_formation.get_formation_max_range_in_meters()
        edd2_max_endurance = empty_drone_delivery_2.drone_formation.max_route_times_in_minutes
        edd2_velocity_per_minute = empty_drone_delivery_1.drone_formation.velocity_meter_per_sec*60.0

        empty_board_1 = EmptyDroneDeliveryBoard([empty_drone_delivery_1])
        empty_board_2 = EmptyDroneDeliveryBoard([empty_drone_delivery_2])

        # Graph definition:
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, edd1_max_range/10.0),
                create_point_2d(0, edd2_max_range/2.1)
            ]),
            time_window_distribution=ExactTimeWindowDistribution([
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=edd1_max_endurance/5.0)))),
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(minutes=edd2_max_endurance)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
        self.delivery_requests = dist.choose_rand(Random(42), amount={DeliveryRequest: 2})
        self.graph = self._create_graph(self.delivery_requests, self.loading_dock, 1/edd2_velocity_per_minute)
        if self.graph.get_max_cost()>edd2_max_endurance/2.0:
            print('Check cost calculation')

        # Match fleet over graph:
        match_config = MatcherConfig(MatcherConfigProperties(
            zero_time=ZERO_TIME,
            first_solution_strategy="or_tools:path_cheapest_arc",
            solver=MatcherSolver(full_name="or_tools:automatic", timeout_sec=30),
            match_constraints=MatcherConstraints(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True),
                time_constraints=TimeConstraints(max_waiting_time=0,
                                                 max_route_time=MAX_OPERATION_TIME,
                                                 count_time_from_zero=False),
                priority_constraints=PriorityConstraints(True)),
            dropped_penalty=1000))

        match_input_1 = MatcherInput(self.graph, empty_board_1, match_config)
        match_input_2 = MatcherInput(self.graph, empty_board_2, match_config)
        matcher_1 = ORToolsMatcher(match_input_1)
        matcher_2 = ORToolsMatcher(match_input_2)
        delivery_board_1 = matcher_1.match()
        delivery_board_2 = matcher_2.match()
        self.assertEqual(1, len(delivery_board_1.drone_deliveries[0].matched_requests))
        self.assertEqual(2, len(delivery_board_2.drone_deliveries[0].matched_requests))

    @staticmethod
    def _create_loading_dock() -> DroneLoadingDock:
        return DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
                                PlatformType.platform_1,
                                TimeWindowExtension(
                                    since=ZERO_TIME,
                                    until=ZERO_TIME.add_time_delta(
                                        TimeDeltaExtension(timedelta(hours=4)))))

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_dock: DroneLoadingDock, factor: float=1.0) -> OperationalGraph:
        graph = OperationalGraph(zero_time=ZERO_TIME.get_internal())
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph, factor)
        return graph
