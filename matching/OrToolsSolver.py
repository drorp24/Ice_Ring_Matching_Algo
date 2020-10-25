"""Vehicles Routing Problem (VRP) with Time Windows."""

from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['time_matrix'] = [
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
    ]
    data['time_windows'] = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ]
    data['num_vehicles'] = 4
    data['depot'] = 0
    data['demands'] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    data['priority'] = [0, 1, 1, 2, 4, 2, 4, 3, 3, 1, 5, 6, 2, 4, 5, 6, 5]
    data['vehicle_capacities'] = [15, 15, 15, 15]
    return data


class OrToolsRoutingSolver:
    def __init__(self, data):
        self._data = data
        self._manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                               data['num_vehicles'], data['depot'])
        self._routing = pywrapcp.RoutingModel(self._manager)
        self._assignment = None
        self._dimension_callback_indices = {}

    def add_priority_objective(self):
        self.add_unary_dimension('priority')
        self.set_arc_dimension('priority')

    def add_time_dimension(self):
        self.add_dimension('time_matrix')
        self._routing.AddDimension(
            self._dimension_callback_indices['time_matrix'],
            30,  # allow waiting time
            30,  # maximum time per vehicle
            False,  # Don't force start cumul to zero.
            'time_matrix')

    def add_demands_constraint(self):
        self.add_unary_dimension('demands')
        self._routing.AddDimensionWithVehicleCapacity(
            self._dimension_callback_indices['demands'],
            5,  # max waiting time
            self._data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'demands')

    def add_unary_dimension(self, dimension_name):
        self._dimension_callback_indices[dimension_name] = self._routing.RegisterUnaryTransitCallback(lambda from_index, to_index, data=self._data: data[dimension_name][self._manager.IndexToNode(from_index)])

    def add_dimension(self, dimension_name):
        self._dimension_callback_indices[dimension_name] = self._routing.RegisterTransitCallback(lambda from_index, to_index, data=self._data: data[dimension_name][self._manager.IndexToNode(from_index)][self._manager.IndexToNode(to_index)])

    def set_arc_dimension(self, dimension_name):
        if dimension_name not in self._dimension_callback_indices:
            raise ValueError(f"Dimension {dimension_name} is unknown.")
        self._routing.SetArcCostEvaluatorOfAllVehicles(self._dimension_callback_indices[dimension_name])

    def print_solution(self):
        """Prints solution on console."""
        # Display routes
        time_dimension = self._routing.GetDimensionOrDie('Time')
        total_time = 0
        total_load = 0
        total_priority = 0
        for vehicle_id in range(self._data['num_vehicles']):
            index = self._routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_load = 0
            route_priority = 0
            while not self._routing.IsEnd(index):
                node_index = self._manager.IndexToNode(index)
                route_load += self._data['demands'][node_index]
                plan_output += ' {0} Load({1}) '.format(node_index, route_load)
                route_priority += self._data['priorities'][node_index]
                plan_output += ' Priority({1}) '.format(node_index, route_priority)
                time_var = time_dimension.CumulVar(index)
                plan_output += 'Time({1},{2}) -> '.format(
                    self._manager.IndexToNode(index), self._assignment.Min(time_var),
                    self._assignment.Max(time_var))
                index = self._assignment.Value(self._routing.NextVar(index))
            plan_output += ' {0} Load({1})\n'.format(self._manager.IndexToNode(index),
                                                     route_load)
            plan_output += '  Priority({1})\n'.format(self._manager.IndexToNode(index),
                                                      route_priority)
            time_var = time_dimension.CumulVar(index)
            plan_output += ' Time({1},{2})\n'.format(self._manager.IndexToNode(index),
                                                     self._assignment.Min(time_var),
                                                     self._assignment.Max(time_var))
            plan_output += 'Time of the route: {}min\n'.format(
                self._assignment.Min(time_var))
            plan_output += 'Load of the route: {}\n'.format(route_load)
            plan_output += 'Priority of the route: {}\n'.format(route_priority)
            print(plan_output)
            total_time += self._assignment.Min(time_var)
            total_load += route_load
            total_priority += route_priority
        print('Total time of all routes: {}min'.format(total_time))
        print('Total load of all routes: {}'.format(total_load))
        print('Total priority of all routes: {}'.format(total_priority))
        # Display dropped nodes.
        dropped_nodes = 'Dropped nodes:'
        for node in range(self._routing.Size()):
            if self._routing.IsStart(node) or self._routing.IsEnd(node):
                continue
            if self._assignment.Value(self._routing.NextVar(node)) == node:
                dropped_nodes += ' {}'.format(self._manager.IndexToNode(node))
        print(dropped_nodes)






def main():
    data = create_data_model()

    solver = OrToolsRoutingSolver(data)
    solver.add_priority_objective()
    solver.add_time_dimension()
    solver.add_demands_constraint()
    solver.add_time_windows_constraint()
    # Add Time Windows constraint.
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0],
                                                data['time_windows'][0][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))


    # priority_callback_index = routing_solver.py.RegisterTransitCallback(priority_callback)
    # routing_solver.py.AddDimension(
    #     priority_callback_index,
    #     5,  # max waiting time
    #     10000,  # vehicle maximum priority - very large because it is not a constraint
    #     True,  # start cumul to zero
    #     priority)
    # priority_dimension = routing_solver.py.GetDimensionOrDie(priority)
    # priority_dimension.SetGlobalSpanCostCoefficient(100)

    # Allow to drop nodes.
    penalty = 5
    for node in range(1, len(data['time_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        print_solution(data, manager, routing, assignment)
    else:
        print("No solution.")


if __name__ == '__main__':
    main()