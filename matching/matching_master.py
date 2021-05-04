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
        if last_start_match_time_delta_in_minutes > self._matcher_input.config.constraints.session_time.max_session_time:
            self._update_delivering_drones_max_route_time(updating_matcher_input.delivering_drones_board,
                                                      last_start_match_time_delta_in_minutes)
            self._run_intermediate_match(drone_deliveries, last_start_match_time_delta_in_minutes, updating_matcher_input, full_time_windows_num -1)
        return DroneDeliveryBoard(drone_deliveries=drone_deliveries,
                                  unmatched_delivery_requests=[UnmatchedDeliveryRequest(i, node.internal_node)
                                                               for i, node in
                                                               enumerate(updating_matcher_input.graph.nodes)
                                                               if isinstance(node.internal_node, DeliveryRequest)])

    def _run_intermediate_match(self, drone_deliveries, start_match_time_delta_in_minutes, updating_matcher_input, session_num):
        self._update_delivering_drones_start_dock_time_window(start_match_time_delta_in_minutes,
                                                              updating_matcher_input)
        self._set_end_loading_docks_initial_time_window(updating_matcher_input.delivering_drones_board, session_num)
        intermediate_delivery_board = create_matcher(updating_matcher_input).match()
        if len(intermediate_delivery_board.drone_deliveries) > 0:
            drone_deliveries.extend(intermediate_delivery_board.drone_deliveries)
        self._remove_matched_requests_from_graph(intermediate_delivery_board, updating_matcher_input)

    @staticmethod
    def _update_delivering_drones_max_route_time(delivering_drones_board, new_max_route_time):
        for delivering_drones in delivering_drones_board.delivering_drones_list:
            delivering_drones.board_level_properties.max_route_time_entire_board = new_max_route_time

    def _set_end_loading_docks_initial_time_window(self, delivering_drones_board, session_num):
        loading_docks = set(delivering_drones.end_loading_dock for delivering_drones in
                            delivering_drones_board.delivering_drones_list)
        original_loading_docks = list(set(delivering_drones.end_loading_dock for delivering_drones in
                                          self._matcher_input.delivering_drones_board.delivering_drones_list))
        for i, loading_dock in enumerate(loading_docks):
            new_until = self._matcher_input.config.zero_time.add_time_delta(
                TimeDeltaExtension(
                    timedelta(
                        minutes=(session_num + 1) * self._matcher_input.config.submatch_time_window_minutes - self._matcher_input.config.constraints.travel_time.reloading_time)))
            if new_until > original_loading_docks[i].time_window.until:
                new_until = original_loading_docks[i].time_window.until

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
