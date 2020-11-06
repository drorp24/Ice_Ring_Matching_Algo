# from ice_ring.diagnoses.monitor import Monitor
# from ice_ring.graph.graph_handler import GraphDataType
# from ice_ring.matching.matching_solution import MatchingSolution

from ortools.constraint_solver import pywrapcp

from matching.matcher import MatchInput
from matching.matching_solution import MatchingSolution
from matching.ortools.ortools_matching_solution import ORToolsMatchingSolution
from matching.ortools.ortools_strategy_factory import ORToolsStrategyFactory


class ORToolsMatcher:

    def __init__(self, match_input: MatchInput):
        if match_input.empty_board.num_of_formations is None:
            return
        self._input = match_input

        self._set_manager()

        self._set_routing()

        self._add_priority_objective()

        self._add_demand_constraints()

        self._add_time_constraints()

        self._add_dropped_penalty()

        self._set_parameters()

    def match(self) -> MatchingSolution:

        # add monitor if needed
        monitor = None
        # if selected_solver.run_monitor:
        #     monitor = self._run_monitor(selected_solver.monitor_iter)

        solution = self._solve()

        # return the solution
        return self._create_match_solution(solution,monitor)

    @property
    def input(self):
        return self._input

    @property
    def routing(self):
        return self._routing

    @property
    def manager(self):
        return self._manager

    # Add Priority objective.
    def _priority_callback(self, from_index):
        """Returns the priority of the node."""
        # Convert from routing variable Index to priorities NodeIndex.
        from_node = self._manager.IndexToNode(from_index)
        return self._input.priorities[from_node]

    # Create and register a transit callback.
    def _time_callback(self, from_index, to_index):
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = self._manager.IndexToNode(from_index)
        to_node = self._manager.IndexToNode(to_index)
        return self._input.graph.travel_weights[from_node][to_node]

    # Add Capacity constraint.
    def _demand_callback(self, from_index):
        # Convert from routing variable Index to demands NodeIndex.
        from_node = self._manager.IndexToNode(from_index)
        return self._input.graph.packeges_per_request[from_node]

    def _solve(self):
        # Solve the problem.
        solution = self._routing.SolveWithParameters(self._search_parameters)
        #print(function_name(self, inspect.currentframe()), "solution objective value=", solution.ObjectiveValue())
        return solution

    def _add_priority_objective(self):
        priority_callback_index = self._routing.RegisterPositiveUnaryTransitCallback(self._priority_callback)
        self._routing.SetArcCostEvaluatorOfAllVehicles(priority_callback_index)

    def _add_dropped_penalty(self):
        # add penalty
        for node in range(1, self._input.empty_board.num_of_formations):
            self._routing.AddDisjunction([self._manager.NodeToIndex(node)], self._input.config.dropped_penalty)

    def _set_routing(self):
        # Create Routing Model.

        # parameters.solver_parameters.trace_propagation = True
        # parameters.solver_parameters.trace_search = True

        self._routing = pywrapcp.RoutingModel(self._manager)

    def _set_manager(self):
        self._manager = pywrapcp.RoutingIndexManager(len(self._input.graph.travel_weights),
                                                     self._input.empty_board.num_of_formations,
                                                     self._input.graph.depos)

    def _add_demand_constraints(self):
        # Register Demand Callback
        demand_callback_index = self._routing.RegisterPositiveUnaryTransitCallback(self._demand_callback)
        self._routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            self._input.empty_board.vehicle_capacities,  # vehicle maximum capacities
            self._input.config.count_capacity_from_zero,  # start cumul to zero
            'Capacity')

    def _add_time_constraints(self):

        # Register Time Callback
        transit_callback_index = self._routing.RegisterTransitCallback(self._time_callback)

        # Add Time Windows constraint.
        time = 'Time'
        self._routing.AddDimension(
            transit_callback_index,
            self._input.config.waiting_time_allowed_min,  # allow waiting time
            self._input.config.max_total_drone_time_min,  # maximum time per vehicle
            self._input.config.count_time_from_zero,  # Don't force start cumul to zero.
            time)
        time_dimension = self._routing.GetDimensionOrDie(time)
        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(self._input.graph.time_windows):
            if location_idx == 0:
                continue
            index = self._manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        # Add time window constraints for each vehicle start node.
        for vehicle_id in range(len(self._input.empty_board.empty_drone_deliveries)):
            index = self._routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(self._input.graph.time_windows[0][0],
                                                    self._input.graph.time_windows[0][1])
        # Instantiate route start and end times to produce feasible times.
        for i in range(len(self._input.empty_board.empty_drone_deliveries)):
            self._routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing.Start(i)))
            self._routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing.End(i)))

    def _set_parameters(self):

        # Setting first solution heuristic.
        self._search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self._search_parameters.first_solution_strategy = ORToolsStrategyFactory.create_first_solution_strategy(
            self._input.config.first_solution_strategy)
        self._search_parameters.local_search_metaheuristic = ORToolsStrategyFactory.create_local_search_solver(
            self._input.config.solver)

        # search_parameters.solution_limit = 5
        self._search_parameters.time_limit.seconds = self._input.config.time_limit_sec
        # self._search_parameters.log_search = self._input.config.log_search

    def _create_match_solution(self, solution, monitor):
        return ORToolsMatchingSolution(self, solution, monitor)
