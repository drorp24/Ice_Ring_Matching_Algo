import uuid
from datetime import timedelta, date, time
from random import Random
from typing import List
from unittest import TestCase

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_delivery import DeliveringDrones
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard, DroneDeliveryBoard
from common.entities.base_entities.drone_formation import DroneFormations, PackageConfigurationOption, \
    DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.priority_distribution import ExactPriorityDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import ExactTimeWindowDistribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.temporal import TimeWindowExtension, DateTimeExtension, TimeDeltaExtension
from common.graph.operational.graph_creator import build_fully_connected_graph
from common.graph.operational.operational_graph import OperationalGraph
from geometry.distribution.geo_distribution import ExactPointLocationDistribution
from geometry.geo_factory import create_point_2d
from matching.constraint_config import ConstraintsConfig, CapacityConstraints, TravelTimeConstraints, \
    PriorityConstraints, SessionTimeConstraints
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.monitor_config import MonitorConfig
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_solver_config import ORToolsSolverConfig
from matching.solver_config import SolverVendor

ZERO_TIME = DateTimeExtension(dt_date=date(2020, 1, 23), dt_time=time(11, 30, 0))


class ORToolsMatcherReloadWithMultipleConfigurationsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls._create_delivery_requests()
        cls.loading_docks = cls._create_loading_docks()
        cls.graph = cls._create_graph(cls.delivery_requests, cls.loading_docks)
        cls.delivering_drones_board = cls._create_delivering_drones_board_with_delivering_drones_with_different_configurations(
            cls.loading_docks)
        cls.match_input = MatcherInput(cls.graph, cls.delivering_drones_board, cls._create_match_config())

    def test_matcher_when_delivering_drones_have_different_configurations_then_reload_successful(self):
        matcher = ORToolsMatcher(self.match_input)
        actual_delivery_board = matcher.match()
        self._assert_all_requests_matched(actual_delivery_board)
        self._assert_drone_deliveries_have_different_configurations(actual_delivery_board)

    def _assert_all_requests_matched(self, actual_delivery_board: DroneDeliveryBoard):
        self.assertEqual(len(self.delivery_requests),
                         actual_delivery_board.get_total_amount_per_package_type().get_package_type_amount(
                             PackageType.LARGE))

    def _assert_drone_deliveries_have_different_configurations(self, actual_delivery_board: DroneDeliveryBoard):
        num_matched_packages_1 = self._get_num_of_matched_packages_of_first_drone_delivery_of_delivering_drones(
            actual_delivery_board, self.delivering_drones_board.delivering_drones_list[0])
        num_matched_packages_2 = self._get_num_of_matched_packages_of_first_drone_delivery_of_delivering_drones(
            actual_delivery_board, self.delivering_drones_board.delivering_drones_list[1])
        self.assertEqual(
            self.delivering_drones_board.delivering_drones_list[0].drone_formation.get_package_type_amount_map()
                .get_package_type_amount(PackageType.LARGE), num_matched_packages_1)
        self.assertEqual(
            self.delivering_drones_board.delivering_drones_list[1].drone_formation.get_package_type_amount_map()
                .get_package_type_amount(PackageType.LARGE), num_matched_packages_2)

    @staticmethod
    def _create_delivery_requests() -> List[DeliveryRequest]:
        dist = build_delivery_request_distribution(
            relative_pdp_location_distribution=ExactPointLocationDistribution([
                create_point_2d(0, 5),
                create_point_2d(0, 5),
                create_point_2d(0, 10),
                create_point_2d(0, 10),
                create_point_2d(0, 15),
                create_point_2d(0, 15),
                create_point_2d(0, 20),
                create_point_2d(0, 20),
                create_point_2d(0, -5),
                create_point_2d(0, -5),
                create_point_2d(0, -10),
                create_point_2d(0, -10),
                create_point_2d(0, -15),
                create_point_2d(0, -15),
                create_point_2d(0, -20),
                create_point_2d(0, -20),
            ]),
            time_window_distribution=ExactTimeWindowDistribution(16 * [
                TimeWindowExtension(
                    since=ZERO_TIME,
                    until=ZERO_TIME.add_time_delta(TimeDeltaExtension(timedelta(hours=2)))),
            ]),
            package_type_distribution=PackageDistribution({PackageType.LARGE: 1}),
            priority_distribution=ExactPriorityDistribution(list(range(1, 17)))
        )
        return dist.choose_rand(Random(42), amount={DeliveryRequest: 16})

    @staticmethod
    def _create_loading_docks() -> [DroneLoadingDock]:
        dock1 = DroneLoadingDock(EntityID.generate_uuid(),
                                 DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 0)),
                                 DroneType.drone_type_1,
                                 TimeWindowExtension(
                                     since=ZERO_TIME,
                                     until=ZERO_TIME.add_time_delta(
                                         TimeDeltaExtension(timedelta(hours=5)))))
        dock2 = DroneLoadingDock(EntityID.generate_uuid(),
                                 DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 10)),
                                 DroneType.drone_type_2,
                                 TimeWindowExtension(
                                     since=ZERO_TIME,
                                     until=ZERO_TIME.add_time_delta(
                                         TimeDeltaExtension(timedelta(hours=5)))))
        return [dock1, dock2]

    @staticmethod
    def _create_graph(delivery_requests: List[DeliveryRequest], loading_docks: [DroneLoadingDock]) -> OperationalGraph:
        graph = OperationalGraph()
        graph.add_drone_loading_docks(loading_docks)
        graph.add_delivery_requests(delivery_requests)
        build_fully_connected_graph(graph)
        return graph

    @staticmethod
    def _create_delivering_drones_board_with_delivering_drones_with_different_configurations(
            loading_docks: [DroneLoadingDock]) -> DeliveringDronesBoard:
        delivering_drones_1 = DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                                  drone_formation=DroneFormations.get_drone_formation(
                                                      DroneFormationType.PAIR,
                                                      PackageConfigurationOption.LARGE_PACKAGES,
                                                      DroneType.drone_type_1),
                                                  start_loading_dock=loading_docks[0],
                                                  end_loading_dock=loading_docks[0])
        delivering_drones_2 = DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                                  drone_formation=DroneFormations.get_drone_formation(
                                                      DroneFormationType.PAIR,
                                                      PackageConfigurationOption.LARGE_PACKAGES,
                                                      DroneType.drone_type_2),
                                                  start_loading_dock=loading_docks[1],
                                                  end_loading_dock=loading_docks[1])
        return DeliveringDronesBoard([delivering_drones_1, delivering_drones_2])

    @staticmethod
    def _create_match_config() -> MatcherConfig:
        return MatcherConfig(
            zero_time=ZERO_TIME,
            solver=ORToolsSolverConfig(first_solution_strategy="PATH_CHEAPEST_ARC",
                                       local_search_strategy="GUIDED_LOCAL_SEARCH", timeout_sec=10),
            constraints=ConstraintsConfig(
                capacity_constraints=CapacityConstraints(count_capacity_from_zero=True, capacity_cost_coefficient=1),
                travel_time_constraints=TravelTimeConstraints(max_waiting_time=0,
                                                              max_route_time=1440,
                                                              count_time_from_zero=False,
                                                              reloading_time=30,
                                                              important_earliest_coeff=1),
                session_time_constraints=SessionTimeConstraints(max_session_time=60),
                priority_constraints=PriorityConstraints(True, priority_cost_coefficient=100)),
            unmatched_penalty=10000,
            reload_per_vehicle=1,
            monitor=MonitorConfig(enabled=False)
        )

    @staticmethod
    def _get_num_of_matched_packages_of_first_drone_delivery_of_delivering_drones(
            actual_delivery_board: DroneDeliveryBoard, delivering_drones: DeliveringDrones):
        for delivery in actual_delivery_board.drone_deliveries:
            if delivery.delivering_drones is delivering_drones:
                return delivery.get_total_package_type_amount_map().get_package_type_amount(PackageType.LARGE)
