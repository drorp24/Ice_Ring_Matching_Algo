from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

from common.entities.package import PackageType
from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import MatcherInput


class ORToolsMatcherConstraints:
    def __init__(self, graph_exporter: OrtoolsGraphExporter, manager: RoutingIndexManager, routing: RoutingModel,
                 matcher_input: MatcherInput):
        self._graph_exporter = graph_exporter
        self._manager = manager
        self._routing = routing
        self._matcher_input = matcher_input

    def add_demand(self):
        for package_type in self._matcher_input.empty_board.package_types():
            callback = getattr(self, "_demand_callback_" + str.lower(package_type.name))
            demand_callback_index = self._routing.RegisterPositiveUnaryTransitCallback(callback)
            self._routing.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                self._matcher_input.config.constraints.time.max_waiting_time,
                self._matcher_input.empty_board.formation_capacities(package_type),
                self._matcher_input.config.constraints.capacity.count_capacity_from_zero,
                'Capacity')

    def _demand_callback_tiny(self, from_index):
        from_node = self._manager.IndexToNode(from_index)
        return self._graph_exporter.export_package_type_demands(self._matcher_input.graph, PackageType.TINY)[
            from_node]

    def _demand_callback_small(self, from_index):
        from_node = self._manager.IndexToNode(from_index)
        return self._graph_exporter.export_package_type_demands(self._matcher_input.graph, PackageType.SMALL)[
            from_node]

    def _demand_callback_medium(self, from_index):
        from_node = self._manager.IndexToNode(from_index)
        return self._graph_exporter.export_package_type_demands(self._matcher_input.graph, PackageType.MEDIUM)[
            from_node]

    def _demand_callback_large(self, from_index):
        from_node = self._manager.IndexToNode(from_index)
        return self._graph_exporter.export_package_type_demands(self._matcher_input.graph, PackageType.LARGE)[
            from_node]

    def add_time(self):
        transit_callback_index = self._routing.RegisterTransitCallback(self._time_callback)
        time = 'Time'
        self._routing.AddDimension(
            transit_callback_index,
            self._matcher_input.config.constraints.time.max_waiting_time,
            self._matcher_input.config.constraints.time.max_route_time,
            self._matcher_input.config.constraints.time.count_time_from_zero,
            time)
        time_dimension = self._routing.GetDimensionOrDie(time)
        time_windows = self._graph_exporter.export_time_windows(self._matcher_input.graph,
                                                                self._matcher_input.config.zero_time)
        self._add_time_window_constraints_for_each_delivery(time_dimension, time_windows)
        self._add_time_window_constraints_for_each_vehicle_start_node(time_dimension, time_windows)
        self._instantiate_route_start_and_end_times_to_produce_feasible_times(time_dimension)

    def _instantiate_route_start_and_end_times_to_produce_feasible_times(self, time_dimension):
        for i in range(len(self._matcher_input.empty_board.empty_drone_deliveries)):
            self._routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing.Start(i)))
            self._routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(self._routing.End(i)))

    def _add_time_window_constraints_for_each_vehicle_start_node(self, time_dimension, time_windows):
        # TODO: Need to allow the start node to be different for each vehicle
        for vehicle_id in range(len(self._matcher_input.empty_board.empty_drone_deliveries)):
            index = self._routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(time_windows[0][0],
                                                    time_windows[0][1])

    def _add_time_window_constraints_for_each_delivery(self, time_dimension, time_windows):
        for location_idx, time_window in enumerate(time_windows):
            # TODO location_idx is not necessary the depot and there could be some depots
            if location_idx == 0:
                continue
            index = self._manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    def _time_callback(self, from_index, to_index):
        from_node = self._manager.IndexToNode(from_index)
        to_node = self._manager.IndexToNode(to_index)
        return self._graph_exporter.export_travel_times(self._matcher_input.graph)[from_node][to_node]

    def add_dropped_penalty(self):
        for node in range(1, len(self._matcher_input.graph.nodes)):
            self._routing.AddDisjunction([self._manager.NodeToIndex(node)],
                                         self._matcher_input.config.dropped_penalty)
