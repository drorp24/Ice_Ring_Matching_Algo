from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import MatchInput

class ORToolsMatcherConstraints:
    def __init__(self, graph_exporter: OrtoolsGraphExporter, manager: RoutingIndexManager, routing: RoutingModel,
                 match_input: MatchInput):
        self._graph_exporter = graph_exporter
        self._manager = manager
        self._routing = routing
        self._match_input = match_input

    def add_demand(self):
        demand_callback_index = self._routing.RegisterPositiveUnaryTransitCallback(self._demand_callback)
        self._routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            self._match_input.empty_board.formation_capacities,
            self._match_input.config.constraints.capacity.count_capacity_from_zero,
            'Capacity')

    def _demand_callback(self, from_index):
        from_node = self._manager.IndexToNode(from_index)
        package_type = \
            self._match_input.empty_board.empty_drone_deliveries[0].drone_formation.get_package_types()[3]
        return self._graph_exporter.export_package_type_demands(self._match_input.graph, package_type)[
            from_node]

    def add_time(self):
        transit_callback_index = self._routing.RegisterTransitCallback(self._time_callback)

        time = 'Time'
        self._routing.AddDimension(
            transit_callback_index,
            self._match_input.config.constraints.time.waiting_time_allowed_min,
            self._match_input.config.constraints.time.max_total_drone_time_min,
            self._match_input.config.constraints.time.count_time_from_zero,
            time)
        time_dimension = self._routing.GetDimensionOrDie(time)
        time_windows = self._graph_exporter.export_time_windows(self._match_input.graph,
                                                                self._match_input.config.zero_time)
        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(time_windows):
            if location_idx == 0:
                continue
            index = self._manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        # Add time window constraints for each vehicle start node.
        for vehicle_id in range(len(self._match_input.empty_board.empty_drone_deliveries)):
            index = self._routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(time_windows[0][0],
                                                    time_windows[0][1])

        # Instantiate route start and end times to produce feasible times.
        for i in range(len(self._match_input.empty_board.empty_drone_deliveries)):
            self._routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing.Start(i)))
            self._routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing.End(i)))

    def _time_callback(self, from_index, to_index):
        from_node = self._manager.IndexToNode(from_index)
        to_node = self._manager.IndexToNode(to_index)
        return self._graph_exporter.export_travel_times(self._match_input.graph)[from_node][to_node]

    def add_dropped_penalty(self):
        for node in range(1, len(self._match_input.graph.nodes)):
            self._routing.AddDisjunction([self._manager.NodeToIndex(node)],
                                         self._match_input.config.dropped_penalty)
