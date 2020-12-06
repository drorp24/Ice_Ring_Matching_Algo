from pathlib import Path
from random import Random
from unittest import TestCase
from datetime import datetime

from common.entities.base_entity import JsonableBaseEntity
from common.entities.customer_delivery import CustomerDeliveryDistribution
from common.entities.delivery_option import DeliveryOptionDistribution
from common.entities.delivery_request import DeliveryRequest
from common.entities.drone import PlatformType
from common.entities.drone_delivery import DroneDelivery, EmptyDroneDelivery, MatchedDeliveryRequest
from common.entities.drone_delivery_board import DroneDeliveryBoard, EmptyDroneDeliveryBoard
from common.entities.drone_formation import FormationSize, FormationOptions, DroneFormations
from common.graph.operational.operational_graph  import OperationalGraph
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.drone_loading_station import DroneLoadingStation
from common.entities.package import PackageDistribution, PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution
from common.entities.temporal import TimeWindowExtension, DateTimeExtension
from common.graph.operational.operational_graph import OperationalGraph, OperationalEdge, OperationalNode, \
    OperationalEdgeAttribs
from geometry.geo_factory import create_point_2d
from matching.matcher import MatchInput, MatchConfig
from matching.ortools.ortools_matcher import ORToolsMatcher


class ORToolsMatcherBasicTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery_requests = cls.create_delivery_requests()
        small_graph = cls.create_graph(cls.delivery_requests)
        empty_board = cls.create_empty_drone_delivery_board()
        do_dict = JsonableBaseEntity.json_to_dict(Path('matching/test/match_config1.json'))
        config = MatchConfig.dict_to_obj(do_dict)
        cls.small_match_input = MatchInput(small_graph, empty_board, config)
        cls.expected_matched_board = cls.create_drone_delivery_board(empty_board.empty_drone_deliveries()[0],
                                                                     empty_board.empty_drone_deliveries()[1],
                                                                     cls.delivery_requests)

    @staticmethod
    def create_delivery_requests():
        pdp_dist = PackageDeliveryPlanDistribution(
            package_type_distribution=PackageDistribution({PackageType.TINY.name: 1}))
        delivery_options = DeliveryOptionDistribution([CustomerDeliveryDistribution(pdp_dist)]).choose_rand(Random(42),
                                                                                                            amount=1,
                                                                                                            num_pdp=1)
        delivery_request_1 = DeliveryRequest(delivery_options=delivery_options,
                                             time_window=TimeWindowExtension(
                                                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
                                                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
                                             priority=1)
        delivery_request_2 = DeliveryRequest(delivery_options=delivery_options,
                                             time_window=TimeWindowExtension(
                                                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 30, 00)),
                                                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 45, 00))),
                                             priority=2)
        return [delivery_request_1, delivery_request_2]

    @staticmethod
    def create_graph(delivery_requests):
        graph = OperationalGraph(zero_time=datetime(2020, 1, 23, 12, 30, 00))
        loading_dock = DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
                                        PlatformType.platform_1,
                                        TimeWindowExtension(since=DateTimeExtension.from_dt(
                                            datetime(2020, 1, 23, 11, 30, 00)),
                                            until=DateTimeExtension.from_dt(
                                                datetime(2020, 1, 23, 16, 30, 00))))
        graph.add_drone_loading_docks([loading_dock])
        graph.add_delivery_requests(delivery_requests)
        graph.add_operational_edges([OperationalEdge(start_node=OperationalNode(loading_dock),
                                                     end_node=OperationalNode(delivery_requests[0]),
                                                     attributes=OperationalEdgeAttribs(3)),
                                     OperationalEdge(start_node=OperationalNode(delivery_requests[0]),
                                                     end_node=OperationalNode(delivery_requests[1]),
                                                     attributes=OperationalEdgeAttribs(5)),
                                     OperationalEdge(start_node=OperationalNode(loading_dock),
                                                     end_node=OperationalNode(delivery_requests[1]),
                                                     attributes=OperationalEdgeAttribs(6))
                                     ])
        return graph

    @staticmethod
    def create_empty_drone_delivery_board():
        empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
            FormationSize.MINI, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))
        empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
            FormationSize.MEDIUM, FormationOptions.TINY_PACKAGES, PlatformType.platform_1))

        return EmptyDroneDeliveryBoard([empty_drone_delivery_1, empty_drone_delivery_2])

    @staticmethod
    def create_drone_delivery_board(empty_drone_delivery_1, empty_drone_delivery_2, delivery_requests):
        drone_delivery_1 = DroneDelivery(empty_drone_delivery_1.id,
                                         empty_drone_delivery_1.drone_formation,
                                         [MatchedDeliveryRequest(delivery_requests[0],
                                                                 DateTimeExtension.from_dt(
                                                                     datetime(2020, 1, 23, 11, 33, 00)))])
        drone_delivery_2 = DroneDelivery(empty_drone_delivery_2.id,
                                         empty_drone_delivery_2.drone_formation,
                                         [MatchedDeliveryRequest(delivery_requests[1],
                                                                 DateTimeExtension.from_dt(
                                                                     datetime(2020, 1, 23, 12, 30, 00)))])
        return DroneDeliveryBoard([drone_delivery_1, drone_delivery_2])

    def test_match(self):
        matcher = ORToolsMatcher(self.small_match_input)
        solution = matcher.match()
        solution.print_solution()
        actual_delivery_board = solution.delivery_board()
        self.assertEqual(self.expected_matched_board, actual_delivery_board)
