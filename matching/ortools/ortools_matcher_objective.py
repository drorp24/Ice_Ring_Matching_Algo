from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher_input import MatcherInput


class ORToolsMatcherObjective:
    def __init__(self, graph_exporter: OrtoolsGraphExporter, manager: RoutingIndexManager, routing: RoutingModel,
                 matcher_input: MatcherInput):
        self._graph_exporter = graph_exporter
        self._manager = manager
        self._routing = routing
        self._matcher_input = matcher_input

    def add_priority(self):
        priority_callback_index = self._routing.RegisterPositiveUnaryTransitCallback(self._priority_callback)
        self._routing.SetArcCostEvaluatorOfAllVehicles(priority_callback_index)

    def _priority_callback(self, from_index):
        from_node = self._manager.IndexToNode(from_index)
        return self._graph_exporter.export_priorities(self._matcher_input.graph)[from_node]
