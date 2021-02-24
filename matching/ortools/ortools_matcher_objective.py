from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher_input import MatcherInput


class ORToolsMatcherObjective:
    def __init__(self, index_manager: RoutingIndexManager, routing_model: RoutingModel,
                 matcher_input: MatcherInput):
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = index_manager
        self._routing_model = routing_model
        self._matcher_input = matcher_input

    def add_priority(self):
        priority_callback_index = self._routing_model.RegisterPositiveUnaryTransitCallback(self._get_priority_callback)
        self._routing_model.SetArcCostEvaluatorOfAllVehicles(priority_callback_index)
        self._routing_model.AddDimension(
            priority_callback_index,
            0,
            1000,
            True,
            'priority')

    def _get_priority_callback(self, from_index):
        from_node = self._index_manager.IndexToNode(from_index)
        return self._graph_exporter.export_priorities(self._matcher_input.graph)[from_node]
