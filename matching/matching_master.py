from copy import deepcopy
from datetime import timedelta
from pathlib import Path

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.temporal import TimeDeltaExtension, TimeWindowExtension
from common.graph.operational.operational_graph import OperationalNode
from matching.initial_solution import Routes, Route
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.ortools.ortools_reloader import ORToolsReloader


class MatchingMaster:
    def __init__(self, matcher_input: MatcherInput):
        self._matcher_input = matcher_input

    def match(self) -> DroneDeliveryBoard:
        if self._matcher_input.config.submatch_time_window_minutes \
                < self._matcher_input.config.constraints.travel_time.max_route_time:
            ret_board = self._match_using_time_greedy()
        else:
            ret_board = ORToolsMatcher(self._matcher_input).match()

        return ret_board

    def match_with_time_greedy_as_init_guess(self, init_guess_path: Path = None) -> DroneDeliveryBoard:
        if init_guess_path:
            init_guess = Routes.from_json(init_guess_path)
        else:
            init_guess = self._create_init_guess_using_time_greedy()
        matcher = ORToolsMatcher(self._matcher_input)
        delivery_board = matcher.match_from_init_solution(initial_routes=init_guess)
        return delivery_board

    def _match_using_time_greedy(self):
        drone_deliveries = []
        copy_of_delivering_drones_board = deepcopy(self._matcher_input.delivering_drones_board)
        copy_of_graph = deepcopy(self._matcher_input.graph)
        updating_matcher_input = MatcherInput(copy_of_graph, copy_of_delivering_drones_board,
                                              self._matcher_input.config)
        full_time_windows_num = int(self._matcher_input.config.constraints.travel_time.max_route_time
                                    / self._matcher_input.config.submatch_time_window_minutes)
        self._update_delivering_drones_max_route_time(updating_matcher_input.delivering_drones_board,
                                                      self._matcher_input.config.submatch_time_window_minutes)
        start_match_time_delta_in_minutes = 0
        for i in range(full_time_windows_num):
            self._run_intermediate_match(drone_deliveries, start_match_time_delta_in_minutes, updating_matcher_input, i)
            start_match_time_delta_in_minutes = self._matcher_input.config.submatch_time_window_minutes

        last_start_match_time_delta_in_minutes = self._matcher_input.config.constraints.travel_time.max_route_time \
                                                 - full_time_windows_num * self._matcher_input.config.submatch_time_window_minutes
        if last_start_match_time_delta_in_minutes > \
                max(self._matcher_input.delivering_drones_board.get_max_session_time_per_drone_delivery()):
            self._update_delivering_drones_max_route_time(updating_matcher_input.delivering_drones_board,
                                                          last_start_match_time_delta_in_minutes)
            self._run_intermediate_match(drone_deliveries, last_start_match_time_delta_in_minutes,
                                         updating_matcher_input, full_time_windows_num - 1)
        return DroneDeliveryBoard(drone_deliveries=drone_deliveries,
                                  unmatched_delivery_requests=[UnmatchedDeliveryRequest(i, node.internal_node)
                                                               for i, node in
                                                               enumerate(updating_matcher_input.graph.nodes)
                                                               if isinstance(node.internal_node, DeliveryRequest)])

    def _create_init_guess_using_time_greedy(self):
        reloader = ORToolsReloader(self._matcher_input)
        init_guess_routes = []
        updating_matcher_input = deepcopy(self._matcher_input)
        updating_matcher_input.config._reload_per_vehicle = 0
        full_time_windows_num = int(self._matcher_input.config.constraints.travel_time.max_route_time
                                    / self._matcher_input.config.submatch_time_window_minutes)
        last_start_match_time_delta_in_minutes = self._matcher_input.config.constraints.travel_time.max_route_time \
                                                 - full_time_windows_num * self._matcher_input.config.submatch_time_window_minutes
        self._update_delivering_drones_max_route_time(updating_matcher_input.delivering_drones_board,
                                                      self._matcher_input.config.submatch_time_window_minutes)
        start_match_time_delta_in_minutes = 0
        for i in range(full_time_windows_num):
            intermediate_routes = self._run_intermediate_match_to_routes(start_match_time_delta_in_minutes,
                                                                         updating_matcher_input, i)

            for route_index, route in enumerate(intermediate_routes.as_list()):
                if i == 0:
                    if len(route) > 0:
                        route.append(reloader.get_vehicle_arrive_indices(route_index)[i])
                        init_guess_routes.append(Route(route))
                elif last_start_match_time_delta_in_minutes <= max(
                        self._matcher_input.delivering_drones_board.get_max_session_time_per_drone_delivery()) \
                        and i == (full_time_windows_num - 1):
                    if len(route) > 0:
                        route.insert(0, reloader.get_vehicle_depart_indices(route_index)[i - 1])
                        init_guess_routes[route_index].indexes.extend(route)
                else:
                    if len(route) > 0:
                        route.insert(0, reloader.get_vehicle_depart_indices(route_index)[i - 1])
                        route.append(reloader.get_vehicle_arrive_indices(route_index)[i])
                        init_guess_routes[route_index].indexes.extend(route)
            start_match_time_delta_in_minutes = self._matcher_input.config.submatch_time_window_minutes
        if last_start_match_time_delta_in_minutes > max(
                self._matcher_input.delivering_drones_board.get_max_session_time_per_drone_delivery()):
            self._update_delivering_drones_max_route_time(updating_matcher_input.delivering_drones_board,
                                                          last_start_match_time_delta_in_minutes)
            intermediate_routes = self._run_intermediate_match_to_routes(last_start_match_time_delta_in_minutes,
                                                                         updating_matcher_input,
                                                                         full_time_windows_num - 1)
            for route_index, route in enumerate(intermediate_routes.as_list()):
                if len(route) > 0:
                    route.insert(0, reloader.get_vehicle_depart_indices(route_index)[full_time_windows_num - 1])
                    init_guess_routes[route_index].indexes.extend(route)
        for route_index, route in enumerate(init_guess_routes):
            if route.indexes[-1] in reloader.reloading_virtual_depos_indices:
                route.indexes.pop()
        return Routes(init_guess_routes)

    def _run_intermediate_match(self, drone_deliveries, start_match_time_delta_in_minutes, updating_matcher_input,
                                session_num):
        self._update_delivering_drones_start_dock_time_window(start_match_time_delta_in_minutes,
                                                              updating_matcher_input)
        self._set_end_loading_docks_initial_time_window(updating_matcher_input.delivering_drones_board, session_num)
        intermediate_delivery_board = create_matcher(updating_matcher_input).match()
        if len(intermediate_delivery_board.drone_deliveries) > 0:
            drone_deliveries.extend(intermediate_delivery_board.drone_deliveries)
        self._remove_matched_requests_from_graph(intermediate_delivery_board, updating_matcher_input)

    def _run_intermediate_match_to_routes(self, start_match_time_delta_in_minutes, updating_matcher_input, session_num):
        self._update_delivering_drones_start_dock_time_window(start_match_time_delta_in_minutes,
                                                              updating_matcher_input)
        self._set_end_loading_docks_initial_time_window(updating_matcher_input.delivering_drones_board, session_num)
        routes = create_matcher(updating_matcher_input).match_to_routes()
        all_intermediate_nodes = updating_matcher_input.graph.nodes
        all_original_nodes = self._matcher_input.graph.nodes
        nodes_to_remove = []
        routes_with_original_idx = []
        for route in routes.as_list():
            route_nodes = [all_intermediate_nodes[index] for index in route]
            nodes_to_remove.extend(route_nodes)
            routes_with_original_idx.append(Route([all_original_nodes.index(node) for node in route_nodes]))
        updating_matcher_input.graph = updating_matcher_input.graph.create_subgraph_without_nodes(nodes_to_remove)
        return Routes(routes_with_original_idx)

    @staticmethod
    def _update_delivering_drones_max_route_time(delivering_drones_board, new_max_route_time):
        for delivering_drones in delivering_drones_board.delivering_drones_list:
            delivering_drones.board_level_properties.max_route_time_entire_board = new_max_route_time

    def _set_end_loading_docks_initial_time_window(self, delivering_drones_board, session_num):
        loading_docks = set(delivering_drones.end_loading_dock for delivering_drones in
                            delivering_drones_board.delivering_drones_list)
        original_loading_docks = list(set(delivering_drones.end_loading_dock for delivering_drones in
                                          self._matcher_input.delivering_drones_board.delivering_drones_list))
        time_delta_from_zero_time_in_minutes = \
            (session_num + 1) * self._matcher_input.config.submatch_time_window_minutes \
            - self._matcher_input.config.constraints.travel_time.reloading_time
        for i, loading_dock in enumerate(loading_docks):
            new_until = self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(
                    timedelta(
                        minutes=time_delta_from_zero_time_in_minutes)))
            if new_until > original_loading_docks[i].time_window.until:
                new_until = original_loading_docks[i].time_window.until

            if new_until < loading_dock.time_window.since:
                new_until = loading_dock.time_window.since
            loading_dock._time_window = \
                TimeWindowExtension(since=loading_dock.time_window.since,
                                    until=new_until)

    @staticmethod
    def _remove_matched_requests_from_graph(intermediate_delivery_board, updating_matcher_input):
        matched_nodes = []
        for delivery in intermediate_delivery_board.drone_deliveries:
            for matched_request in delivery.matched_requests:
                matched_nodes.append(OperationalNode(matched_request.delivery_request))
        updating_matcher_input.graph = updating_matcher_input.graph.create_subgraph_without_nodes(matched_nodes)

    def _update_delivering_drones_start_dock_time_window(self, start_match_time_delta_in_minutes,
                                                         updating_matcher_input):
        loading_docks = set(delivering_drones.start_loading_dock for delivering_drones in
                            updating_matcher_input.delivering_drones_board.delivering_drones_list)
        original_loading_docks = list(set(delivering_drones.start_loading_dock for delivering_drones in
                                          self._matcher_input.delivering_drones_board.delivering_drones_list))
        for i, loading_dock in enumerate(loading_docks):
            new_until = loading_dock.time_window.until.add_time_delta(
                TimeDeltaExtension(
                    timedelta(minutes=start_match_time_delta_in_minutes)))
            if new_until > original_loading_docks[i].time_window.until:
                new_until = original_loading_docks[i].time_window.until

            new_since = loading_dock.time_window.since.add_time_delta(
                TimeDeltaExtension(
                    timedelta(minutes=start_match_time_delta_in_minutes)))
            if new_since > new_until:
                new_since = new_until

            loading_dock._time_window = \
                TimeWindowExtension(since=new_since,
                                    until=new_until)
