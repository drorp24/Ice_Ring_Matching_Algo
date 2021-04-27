from copy import copy, deepcopy
from datetime import timedelta

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.temporal import TimeDeltaExtension, TimeWindowExtension
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher


class MatchingMaster:
    def __init__(self, matcher_input: MatcherInput):
        self._matcher_input = matcher_input

    def match(self) -> DroneDeliveryBoard:
        if self._matcher_input.config.submatch_time_window_minutes < self._matcher_input.config.constraints.travel_time.max_route_time:
            ret_board = self._match_using_time_greedy()
        else:
            ret_board = ORToolsMatcher(self._matcher_input).match()

        return ret_board

    def _match_using_time_greedy(self):
            drone_deliveries = []
            updating_matcher_input = deepcopy(self._matcher_input)
            time_windows_num = int(self._matcher_input.config.constraints.travel_time.max_route_time \
                                   / self._matcher_input.config.submatch_time_window_minutes)
            start_match_time_delta_in_minutes = 0
            for i in range(time_windows_num):
                for delivering_drones in updating_matcher_input.delivering_drones_board.delivering_drones_list:
                    delivering_drones.board_level_properties.max_route_time_entire_board = self._matcher_input.config.submatch_time_window_minutes
                    new_since = delivering_drones.start_loading_dock.time_window.since.add_time_delta(
                        TimeDeltaExtension(
                            timedelta(minutes=start_match_time_delta_in_minutes)))
                    if new_since > delivering_drones.start_loading_dock.time_window.until:
                        new_since = delivering_drones.start_loading_dock.time_window.until
                    delivering_drones._start_loading_dock._time_window = \
                        TimeWindowExtension(since=new_since,
                                            until=delivering_drones.start_loading_dock.time_window.until)
                intermediate_delivery_board = ORToolsMatcher(updating_matcher_input).match()
                if len(intermediate_delivery_board.drone_deliveries) > 0:
                    drone_deliveries.extend(intermediate_delivery_board.drone_deliveries)
                for delivery in intermediate_delivery_board.drone_deliveries:
                    updating_matcher_input.graph.remove_delivery_requests(
                        [matched_request.delivery_request for matched_request in delivery.matched_requests])
                start_match_time_delta_in_minutes = self._matcher_input.config.submatch_time_window_minutes

            last_start_match_time_delta_in_minutes = self._matcher_input.config.constraints.travel_time.max_route_time \
                                                     - time_windows_num * self._matcher_input.config.submatch_time_window_minutes
            for delivering_drones in updating_matcher_input.delivering_drones_board.delivering_drones_list:
                delivering_drones.board_level_properties.max_route_time_entire_board = last_start_match_time_delta_in_minutes
                new_since = delivering_drones.start_loading_dock.time_window.since.add_time_delta(
                    TimeDeltaExtension(
                        timedelta(minutes=start_match_time_delta_in_minutes)))
                if new_since > delivering_drones.start_loading_dock.time_window.until:
                    new_since = delivering_drones.start_loading_dock.time_window.until
                delivering_drones._start_loading_dock._time_window = \
                    TimeWindowExtension(since=new_since,
                                        until=delivering_drones.start_loading_dock.time_window.until)
            intermediate_delivery_board = ORToolsMatcher(updating_matcher_input).match()
            if len(intermediate_delivery_board.drone_deliveries) > 0:
                drone_deliveries.extend(intermediate_delivery_board.drone_deliveries)
            for delivery in intermediate_delivery_board.drone_deliveries:
                updating_matcher_input.graph.remove_delivery_requests(
                    [matched_request.delivery_request for matched_request in delivery.matched_requests])
            return DroneDeliveryBoard(drone_deliveries, [UnmatchedDeliveryRequest(i, node.internal_node)
                                                              for i, node in enumerate(updating_matcher_input.graph.nodes)
                                                              if isinstance(node.internal_node, DeliveryRequest)])
