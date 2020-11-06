# from ice_ring.graph.graph_handler import GraphDataType
from matching.matching_solution import MatchingSolution, MatchingSolutionData

from matching.matcher import Matcher


class ORToolsMatchingSolution(MatchingSolution):

    def __init__(self, matcher: Matcher, solution: dict, monitor):
        super().__init__(matcher, solution, monitor)

    def _save_routing(self):

        input = self._matching_handler.input
        routing = self._matching_handler.routing
        manager = self._matching_handler.manager

        # Save dropped
        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if self.solution.Value(routing.NextVar(node)) == node:
                self._data_matched[MatchingSolutionData.dropped_nodes].append(node)
        # Save solution details into matching_solution for plot and print usage
        time_dimension = routing.GetDimensionOrDie('Time')
        for vehicle_id in range(input.empty_board.num_of_formations):
            nodes_in_route = []
            node_service_time = {}
            node_route_load = {}
            node_route_priority = {}
            index = routing.Start(vehicle_id)
            route_load = 0
            route_priority = 0
            while not routing.IsEnd(index):
                time_var = time_dimension.CumulVar(index)
                node_index = manager.IndexToNode(index)

                nodes_in_route.append(node_index)
                route_load += input.graph.packeges_per_request[node_index]

                node_service_time[node_index] = (self._solution.Min(time_var),
                                                 self._solution.Max(time_var))
                route_priority += input.graph.priorities[node_index]
                node_route_load[node_index] = route_load
                node_route_priority[node_index] = route_priority
                index = self._solution.Value(routing.NextVar(index))

            time_var = time_dimension.CumulVar(index)
            node_index = manager.IndexToNode(index)
            nodes_in_route.append(node_index)

            node_service_time[node_index] = (self._solution.Min(time_var),
                                             self._solution.Max(time_var))
            node_route_load[node_index] = route_load
            node_route_priority[node_index] = route_priority

            self._data_matched[MatchingSolutionData.vehicle_route].append(nodes_in_route)
            self._data_matched[MatchingSolutionData.node_service_time][
                vehicle_id] = node_service_time
            self._data_matched[MatchingSolutionData.node_route_load][vehicle_id] = node_route_load
            self._data_matched[MatchingSolutionData.node_route_priority][vehicle_id] = node_route_priority
            self._data_matched[
                MatchingSolutionData.total_time] += self._solution.Min(time_var)
            self._data_matched[MatchingSolutionData.total_load] += route_load
            self._data_matched[MatchingSolutionData.total_priority] += route_priority

    def print_solution(self):
        # print solution based on the data_matched
        manager = self._matching_handler.manager

        "Prints solution on console"
        if not self._solution:
            return

        dropped_nodes = []
        for node in self.dropped:
            dropped_nodes.append(manager.IndexToNode(node))
        print(f'Dropped nodes ({len(dropped_nodes)}): {dropped_nodes}')

        for vehicle_id, vehicle_route in enumerate(self.vehicle_route):

            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)

            time = (0, 0)
            route_load = 0
            route_priority = 0
            for idx, node_index in enumerate(vehicle_route):
                if idx > 0:
                    time = self.node_service_time[vehicle_id][node_index]
                    route_load = self.node_route_load[vehicle_id][node_index]
                    route_priority = self.node_route_priority[vehicle_id][node_index]
                plan_output += ' {0} Time({1},{2}) Load({3}) priority({4})'.format(node_index, time[0], time[1], route_load, route_priority)
                if idx < len(vehicle_route) - 1:
                    plan_output += '->'

            plan_output += "\n"
            plan_output += 'Time of the route: {}min\n'.format(time[0])
            plan_output += 'Load of the route: {}\n'.format(route_load)
            plan_output += 'Priority of the route: {}\n'.format(route_priority)
            print(plan_output)

        print('Total time of all routes: {}min'.format(self.total_time))
        print('Total load of all routes: {}'.format(self.total_load))
        print('Total priority of all routes: {}'.format(self.total_priority))

    def _print_solution_debug(self):
        # print solution based on the solution received

        input = self._matching_handler.input
        routing = self._matching_handler.routing
        manager = self._matching_handler.manager

        print("********* print_solution_debug start *************")

        dropped_nodes = 'Dropped nodes:'

        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if self._solution.Value(routing.NextVar(node)) == node:
                dropped_nodes += ' {}'.format(manager.IndexToNode(node))
                # input["dropped"].append(node)
        print(dropped_nodes)
        time_dimension = routing.GetDimensionOrDie('Time')
        total_time = 0
        total_load = 0
        for vehicle_id in range(input.empty_board.num_of_formations):
            nodes_in_route = []
            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_load = 0
            while not routing.IsEnd(index):
                time_var = time_dimension.CumulVar(index)
                node_index = manager.IndexToNode(index)
                nodes_in_route.append(node_index)
                route_load += input.graph.packeges_per_request[node_index]
                plan_output += ' {0} Time({1},{2}) Load({3})-> '.format(node_index, self._solution.Min(time_var),
                                                                        self._solution.Max(time_var), route_load)
                # input["solution"][node_index] = (solution.Min(time_var), solution.Max(time_var))
                print("route_load", route_load)
                index = self._solution.Value(routing.NextVar(index))
            time_var = time_dimension.CumulVar(index)
            # input["route"].append(nodes_in_route)

            plan_output += '{0} Time({1},{2}) Load({3})\n'.format(manager.IndexToNode(index),
                                                                  self._solution.Min(time_var),
                                                                  self._solution.Max(time_var), route_load)
            plan_output += 'Time of the route: {}min\n'.format(self._solution.Min(time_var))
            plan_output += 'Load of the route: {}\n'.format(route_load)
            print(plan_output)
            total_time += self._solution.Min(time_var)
            total_load += route_load
        print('Total time of all routes: {}min'.format(total_time))
        print('Total load of all routes: {}'.format(total_load))
        print("********* print_solution_debug end *************")
