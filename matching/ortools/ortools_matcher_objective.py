from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher_input import MatcherInput


class ORToolsMatcherObjective:
    def __init__(self, index_manager: RoutingIndexManager, routing_model: RoutingModel,
                 matcher_input: MatcherInput, reloading_virtual_depos_indices: [int]):
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input
        self._reloading_virtual_depos_indices = reloading_virtual_depos_indices

    def add_priority(self):
        priority_callback_index = self._routing_model.RegisterPositiveUnaryTransitCallback(self._get_priority_callback)
        self._routing_model.SetArcCostEvaluatorOfAllVehicles(priority_callback_index)

    def _get_priority_callback(self, from_index):
        from_node = self._index_manager.IndexToNode(from_index)
        if from_node in self._reloading_virtual_depos_indices:
            from_node = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)[0]
        return self._graph_exporter.export_priorities(self._matcher_input.graph)[from_node]
