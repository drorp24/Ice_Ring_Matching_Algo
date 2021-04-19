from functools import lru_cache
from ortools.constraint_solver.pywrapcp import RoutingModel

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_index_manager_wrapper import OrToolsIndexManagerWrapper
from matching.ortools.ortools_matcher import Reloader
from matching.ortools.ortools_matcher_constraints import OrToolsDimensionDescription


class ORToolsMatcherObjective:
    def __init__(self, index_manager: OrToolsIndexManagerWrapper, routing_model: RoutingModel,
                 matcher_input: MatcherInput, reloader: Reloader):
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input
        self._reloader = reloader

    def add_priority(self):
        priority_callback_index = self._routing_model.RegisterUnaryTransitCallback(
            self.create_priority_evaluator())
        self._routing_model.SetArcCostEvaluatorOfAllVehicles(priority_callback_index)
        self._routing_model.AddDimension(
            priority_callback_index,
            0,
            self._matcher_input.config.constraints.priority.priority_cost_coefficient * 10000,
            True,
            OrToolsDimensionDescription.priority.value)

    def create_priority_evaluator(self):

        def priority(_from_node):
            if _from_node in self._reloader.reloading_virtual_depos_indices:
                vehicle_of_node = self._reloader.get_reloading_depot_vehicle(_from_node)
                dock = self._matcher_input.delivering_drones_board.delivering_drones_list[
                                                                                    vehicle_of_node].start_loading_dock
                _from_node = self._graph_exporter.get_node_graph_index(self._matcher_input.graph, dock)
            _priority = self._graph_exporter.export_priorities(self._matcher_input.graph)[_from_node] * \
                self._matcher_input.config.constraints.priority.priority_cost_coefficient
            return _priority

        _priorities = {}
        for from_node in range(self._reloader.num_of_nodes):
            _priorities[from_node] = int(priority(from_node))

        @lru_cache()
        def priority_evaluator(_from_index):
            return _priorities[self._index_manager.index_to_node(_from_index)]

        return priority_evaluator
