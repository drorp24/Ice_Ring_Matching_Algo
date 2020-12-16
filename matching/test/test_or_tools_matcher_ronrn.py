# from datetime import datetime, date, time
# from pathlib import Path
# from random import Random
# from unittest import TestCase
# from uuid import UUID
#
# from common.entities.base_entity import JsonableBaseEntity
# from common.entities.customer_delivery import CustomerDeliveryDistribution, CustomerDelivery
# from common.entities.delivery_option import DeliveryOptionDistribution, DeliveryOption
# from common.entities.delivery_request import DeliveryRequest
# from common.entities.drone import PlatformType
# from common.entities.drone_delivery import EmptyDroneDelivery, DroneDelivery, MatchedDeliveryRequest, \
#     MatchedDroneLoadingDock
# from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard
# from common.entities.drone_formation import FormationSize, FormationOptions, DroneFormations
# from common.entities.drone_loading_dock import DroneLoadingDock
# from common.entities.drone_loading_station import DroneLoadingStation
# from common.entities.package import PackageDistribution, PackageType
# from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution, PackageDeliveryPlan
# from common.entities.temporal import TimeWindowExtension, DateTimeExtension
# from common.graph.operational.graph_creator import build_fully_connected_graph
# from common.graph.operational.operational_graph import OperationalGraph, OperationalEdge, OperationalNode, \
#     OperationalEdgeAttribs
# from common.math.angle import Angle, AngleUnit
# from geometry.geo_factory import create_point_2d
# from matching.matcher_input import MatcherInput
# from matching.matcher_config import MatcherConfig, MatcherConfigProperties, MatcherSolver, MatcherConstraints, \
#     CapacityConstraints, TimeConstraints, PriorityConstraints
# from matching.ortools.ortools_matcher import ORToolsMatcher
#
#
# class ORToolsMatcherBasicTestCase(TestCase):
#     @classmethod
#     def setUpClass(cls):
#
#     def test_matcher_when_time_windows_different(self):
#         delivery_request_1 = DeliveryRequest(
#             delivery_options=[DeliveryOption([CustomerDelivery([
#                 PackageDeliveryPlan(UUID(int=1),
#                                     create_point_2d(0, 5),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     PackageType.LARGE)])])],
#             time_window=TimeWindowExtension(
#                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
#                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
#             priority=1)
#         delivery_request_2 = DeliveryRequest(
#             delivery_options=[DeliveryOption([CustomerDelivery([
#                 PackageDeliveryPlan(UUID(int=2),
#                                     create_point_2d(0, 10),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     PackageType.LARGE)])])],
#             time_window=TimeWindowExtension(
#                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 30, 00)),
#                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 13, 00, 00))),
#             priority=1)
#
#         delivery_requests = [delivery_request_1, delivery_request_2]
#
#         # ------------------------------------ graph ------------------------------------------
#         loading_dock = DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
#                                         PlatformType.platform_1,
#                                         TimeWindowExtension(
#                                             since=DateTimeExtension.from_dt(
#                                                 datetime(2020, 1, 23, 11, 30, 00)),
#                                             until=DateTimeExtension.from_dt(
#                                                 datetime(2020, 1, 23, 16, 30, 00))))
#         graph = OperationalGraph(zero_time=datetime(2020, 1, 23, 11, 30, 00))
#         graph.add_drone_loading_docks([loading_dock])
#         graph.add_delivery_requests(delivery_requests)
#         build_fully_connected_graph(graph)
#
#         # ------------------------------------ empty_board ------------------------------------------
#         empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
#             FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))
#         empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
#             FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))
#         empty_board = EmptyDroneDeliveryBoard([empty_drone_delivery_1, empty_drone_delivery_2])
#
#         # ------------------------------------ match_input ------------------------------------------
#         match_input = MatcherInput(graph, empty_board,
#                                    MatcherConfig(self.match_config_properties))
#
#         # ------------------------------------ expected_matched_board ------------------------------------------
#         drone_delivery_1 = DroneDelivery(empty_drone_delivery_1.id,
#                                          empty_drone_delivery_1.drone_formation,
#                                          [MatchedDeliveryRequest(
#                                              graph_index=1,
#                                              delivery_request=delivery_requests[0],
#                                              matched_delivery_option_index=0,
#                                              delivery_min_time=DateTimeExtension.from_dt(
#                                                  datetime(2020, 1, 23, 11, 35, 00)),
#                                              delivery_max_time=DateTimeExtension.from_dt(
#                                                  datetime(2020, 1, 23, 11, 35, 00)))
#                                          ],
#                                          start_drone_loading_docks=MatchedDroneLoadingDock(
#                                              graph_index=0,
#                                             drone_loading_dock=loading_dock,
#                                             delivery_min_time: DateTimeExtension
#                                             delivery_max_time: DateTimeExtension
# ,
#         [0]),
#                                          end_drone_loading_docks=[0])
#         drone_delivery_2 = DroneDelivery(empty_drone_delivery_2.id,
#                                          empty_drone_delivery_2.drone_formation,
#                                          [MatchedDeliveryRequest(
#                                              graph_index=2,
#                                              delivery_request=delivery_requests[1],
#                                              matched_delivery_option_index=0,
#                                              delivery_min_time=DateTimeExtension.from_dt(
#                                                  datetime(2020, 1, 23, 12, 30, 00)),
#                                              delivery_max_time=DateTimeExtension.from_dt(
#                                                  datetime(2020, 1, 23, 12, 30, 00)))
#                                          ])
#         expected_matched_board = DroneDeliveryBoard(drone_deliveries = [drone_delivery_1, drone_delivery_2],
#                                                     dropped_delivery_request = [])
#
#         matcher = ORToolsMatcher(match_input)
#         actual_delivery_board = matcher.match()
#         print(actual_delivery_board)
#
#         self.assertEqual(expected_matched_board, actual_delivery_board)
#
#
#     def test_matcher_when_priority_is_different_then_output_is_different(self):
#         # ------------------------------ delivery_requests -----------------------------------------------
#
#         # pdp_dist = PackageDeliveryPlanDistribution(
#         #     drop_point_distribution=UniformPointInBboxDistribution(min_x=5, max_x=5, min_y=5, max_y=5),
#         #     package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
#         # delivery_options = DeliveryOptionDistribution([CustomerDeliveryDistribution(pdp_dist)]).choose_rand(Random(42),
#         #                                                                                                     amount=1,
#         #                                                                                                     num_pdp=1)
#         delivery_request_1 = DeliveryRequest(
#             delivery_options=[DeliveryOption([CustomerDelivery([
#                 PackageDeliveryPlan(UUID(int=1),
#                                     create_point_2d(0, 5),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     PackageType.LARGE)])])],
#             time_window=TimeWindowExtension(
#                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
#                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
#             priority=1)
#         delivery_request_2 = DeliveryRequest(
#             delivery_options=[DeliveryOption([CustomerDelivery([
#                 PackageDeliveryPlan(UUID(int=2),
#                                     create_point_2d(0, 10),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     PackageType.LARGE)])])],
#             time_window=TimeWindowExtension(
#                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
#                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
#             priority=2)
#         delivery_request_3 = DeliveryRequest(
#             delivery_options=[DeliveryOption([CustomerDelivery([
#                 PackageDeliveryPlan(UUID(int=3),
#                                     create_point_2d(0, 15),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     PackageType.LARGE)])])],
#             time_window=TimeWindowExtension(
#                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
#                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
#             priority=1)
#
#         delivery_requests = [delivery_request_1, delivery_request_2, delivery_request_3]
#
#         # ------------------------------------ graph ------------------------------------------
#         loading_dock = DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
#                                         PlatformType.platform_1,
#                                         TimeWindowExtension(
#                                             since=DateTimeExtension.from_dt(
#                                                 datetime(2020, 1, 23, 11, 30, 00)),
#                                             until=DateTimeExtension.from_dt(
#                                                 datetime(2020, 1, 23, 16, 30, 00))))
#         graph = OperationalGraph(zero_time=datetime(2020, 1, 23, 11, 30, 00))
#         graph.add_drone_loading_docks([loading_dock])
#         graph.add_delivery_requests(delivery_requests)
#         build_fully_connected_graph(graph)
#
#         # ------------------------------------ empty_board ------------------------------------------
#         empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
#             FormationSize.MINI, FormationOptions.LARGE_PACKAGES, PlatformType.platform_1))
#         empty_board = EmptyDroneDeliveryBoard([empty_drone_delivery_1])
#
#         # ------------------------------------ match_input ------------------------------------------
#         match_input = MatcherInput(graph, empty_board,
#                                    MatcherConfig(self.match_config_properties))
#
#         # ------------------------------------ expected_matched_board ------------------------------------------
#         drone_delivery_1 = DroneDelivery(empty_drone_delivery_1.id,
#                                          empty_drone_delivery_1.drone_formation,
#                                          [MatchedDeliveryRequest(
#                                              graph_index=3,
#                                              delivery_request=delivery_requests[2],
#                                              matched_delivery_option_index=0,
#                                              delivery_min_time=DateTimeExtension.from_dt(
#                                                  datetime(2020, 1, 23, 11, 45, 00)),
#                                              delivery_max_time=DateTimeExtension.from_dt(
#                                                  datetime(2020, 1, 23, 11, 45, 00))),
#                                              MatchedDeliveryRequest(
#                                                  graph_index=1,
#                                                  delivery_request=delivery_requests[0],
#                                                  matched_delivery_option_index=0,
#                                                  delivery_min_time=DateTimeExtension.from_dt(
#                                                      datetime(2020, 1, 23, 11, 55, 00)),
#                                                  delivery_max_time=DateTimeExtension.from_dt(
#                                                      datetime(2020, 1, 23, 11, 55, 00)))
#                                          ],
#                                          start_drone_loading_docks=[0],
#                                          end_drone_loading_docks=[0])
#         expected_matched_board = DroneDeliveryBoard([drone_delivery_1])
#
#         matcher = ORToolsMatcher(match_input)
#         solution = matcher.match()
#         solution.print_solution()
#         actual_delivery_board = solution.delivery_board()
#         self.assertEqual(expected_matched_board, actual_delivery_board)
#
#     def test_matcher_when_drop_penalty_zero_then_no_deliveries(self):
#         self.match_config_properties.dropped_penalty = 0
#         self.small_match_input = MatcherInput(self.small_graph, self.empty_board,
#                                               MatcherConfig(self.match_config_properties))
#         empty_drone_delivery_1 = self.empty_board.empty_drone_deliveries()[0]
#         empty_drone_delivery_2 = self.empty_board.empty_drone_deliveries()[1]
#         drone_delivery_1 = DroneDelivery(empty_drone_delivery_1.id,
#                                          empty_drone_delivery_1.drone_formation,
#                                          [])
#         drone_delivery_2 = DroneDelivery(empty_drone_delivery_2.id,
#                                          empty_drone_delivery_2.drone_formation,
#                                          [])
#         expected_matched_board = DroneDeliveryBoard([drone_delivery_1, drone_delivery_2])
#
#         matcher = ORToolsMatcher(self.small_match_input)
#
#         solution = matcher.match()
#         solution.print_solution()
#         actual_delivery_board = solution.delivery_board()
#         self.assertEqual(expected_matched_board, actual_delivery_board)
#
#     def test_matcher_when_fleet_has_multiple_package_types(self):
#         # ------------------------------ delivery_requests -----------------------------------------------
#
#         # pdp_dist = PackageDeliveryPlanDistribution(
#         #     drop_point_distribution=UniformPointInBboxDistribution(min_x=5, max_x=5, min_y=5, max_y=5),
#         #     package_type_distribution=PackageDistribution({PackageType.LARGE.name: 1}))
#         # delivery_options = DeliveryOptionDistribution([CustomerDeliveryDistribution(pdp_dist)]).choose_rand(Random(42),
#         #                                                                                                     amount=1,
#         #                                                                                                     num_pdp=1)
#         delivery_request_1 = DeliveryRequest(
#             delivery_options=[DeliveryOption([CustomerDelivery([
#                 PackageDeliveryPlan(UUID(int=1),
#                                     create_point_2d(0, 5),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     PackageType.SMALL)])])],
#             time_window=TimeWindowExtension(
#                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
#                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
#             priority=1)
#         delivery_request_2 = DeliveryRequest(
#             delivery_options=[DeliveryOption([CustomerDelivery([
#                 PackageDeliveryPlan(UUID(int=2),
#                                     create_point_2d(0, 10),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     Angle(45, AngleUnit.DEGREE),
#                                     PackageType.MEDIUM)])])],
#             time_window=TimeWindowExtension(
#                 since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 11, 30, 00)),
#                 until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 12, 00, 00))),
#             priority=2)
#
#         delivery_requests = [delivery_request_1, delivery_request_2]
#
#         # ------------------------------------ graph ------------------------------------------
#         loading_dock = DroneLoadingDock(DroneLoadingStation(create_point_2d(0, 0)),
#                                         PlatformType.platform_1,
#                                         TimeWindowExtension(
#                                             since=DateTimeExtension.from_dt(
#                                                 datetime(2020, 1, 23, 11, 30, 00)),
#                                             until=DateTimeExtension.from_dt(
#                                                 datetime(2020, 1, 23, 16, 30, 00))))
#         graph = OperationalGraph(zero_time=datetime(2020, 1, 23, 11, 30, 00))
#         graph.add_drone_loading_docks([loading_dock])
#         graph.add_delivery_requests(delivery_requests)
#         build_fully_connected_graph(graph)
#
#         # ------------------------------------ empty_board ------------------------------------------
#         empty_drone_delivery_1 = EmptyDroneDelivery("edd_1", DroneFormations.get_drone_formation(
#             FormationSize.MINI, FormationOptions.MEDIUM_PACKAGES, PlatformType.platform_1))
#         empty_drone_delivery_2 = EmptyDroneDelivery("edd_2", DroneFormations.get_drone_formation(
#             FormationSize.MINI, FormationOptions.SMALL_PACKAGES, PlatformType.platform_1))
#         empty_board = EmptyDroneDeliveryBoard([empty_drone_delivery_1, empty_drone_delivery_2])
#
#         # ------------------------------------ match_input ------------------------------------------
#         match_input = MatcherInput(graph, empty_board,
#                                    MatcherConfig(self.match_config_properties))
#
#         # ------------------------------------ expected_matched_board ------------------------------------------
#         drone_delivery_1 = DroneDelivery(empty_drone_delivery_1.id,
#                                          empty_drone_delivery_1.drone_formation,
#                                          [MatchedDeliveryRequest(delivery_requests[0],
#                                                                  DateTimeExtension.from_dt(
#                                                                      datetime(2020, 1, 23, 11, 45, 00)))
#                                           ])
#         drone_delivery_2 = DroneDelivery(empty_drone_delivery_2.id,
#                                          empty_drone_delivery_2.drone_formation,
#                                          [MatchedDeliveryRequest(delivery_requests[1],
#                                                                  DateTimeExtension.from_dt(
#                                                                      datetime(2020, 1, 23, 11, 45, 00)))
#                                           ])
#         expected_matched_board = DroneDeliveryBoard([drone_delivery_1, drone_delivery_2])
#
#         matcher = ORToolsMatcher(match_input)
#         solution = matcher.match()
#         solution.print_solution()
#         actual_delivery_board = solution.delivery_board()
#         self.assertEqual(expected_matched_board, actual_delivery_board)
