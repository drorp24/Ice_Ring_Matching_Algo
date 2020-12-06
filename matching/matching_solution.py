import enum

from common.entities.drone_delivery_board import DroneDeliveryBoard


class MatchingSolutionData(enum.Enum):
    dropped_nodes = 'dropped_nodes'
    node_service_time = 'node_service_time'
    node_route_load = 'node_route_load'
    node_route_priority = 'node_route_priority'
    vehicle_route = 'vehicle_route'  # route for each vehicle
    total_time = 'total_time'
    total_load = 'total_load'
    total_priority = 'total_priority'
    total_capacity = 'total_capacity'


class MatchingSolution:
    def __init__(self,matching_handler,solution):
        self._solution = solution
        self._matching_handler = matching_handler

        # __data_matched - dict of MatchingSolutionData
        self._data_matched = {
            MatchingSolutionData.dropped_nodes: [],
            MatchingSolutionData.node_service_time: {},
            MatchingSolutionData.node_route_load: {},
            MatchingSolutionData.node_route_priority: {},
            MatchingSolutionData.vehicle_route: [],
            MatchingSolutionData.total_time: 0,
            MatchingSolutionData.total_load: 0,
            MatchingSolutionData.total_priority: 0,
            MatchingSolutionData.total_capacity: 0
        }

        self._save_routing()

        # self.print_solution_debug()
        # print("monitor ", self._monitor)


    @property
    def solution(self):
        return self._solution

    @property
    def matching_handler(self):
        return self._matching_handler

    @property
    def dropped(self):
        return self._data_matched[MatchingSolutionData.dropped_nodes]

    @property
    def node_service_time(self):
        return self._data_matched[MatchingSolutionData.node_service_time]

    @property
    def node_route_load(self):
        return self._data_matched[MatchingSolutionData.node_route_load]

    @property
    def node_route_priority(self):
        return self._data_matched[MatchingSolutionData.node_route_priority]

    @property
    def vehicle_route(self):
        return self._data_matched[MatchingSolutionData.vehicle_route]

    @property
    def total_time(self):
        return self._data_matched[MatchingSolutionData.total_time]

    @property
    def total_load(self):
        return self._data_matched[MatchingSolutionData.total_load]

    @property
    def total_priority(self):
        return self._data_matched[MatchingSolutionData.total_priority]

    @property
    def total_capacity(self):
        return self._data_matched[MatchingSolutionData.total_capacity]

    def delivery_board(self) -> DroneDeliveryBoard:
        pass

    def _save_routing(self):
        pass

    def print_solution(self):
        # print solution based on the data_matched
        pass

    def print_solution_debug(self):
        # print solution based on the solution received
         pass
