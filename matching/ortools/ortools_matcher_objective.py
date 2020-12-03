from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher import MatchInput


class ORToolsMatcherObjective:
    def __init__(self, graph_exporter: OrtoolsGraphExporter, manager: RoutingIndexManager, routing: RoutingModel,
                 match_input: MatchInput):
        self._graph_exporter = graph_exporter
        self._manager = manager
        self._routing = routing
        self._match_input = match_input

    def add_priority(self):
        priority_callback_index = self._routing.RegisterPositiveUnaryTransitCallback(self._priority_callback)
        self._routing.SetArcCostEvaluatorOfAllVehicles(priority_callback_index)

    def _priority_callback(self, from_index):
        from_node = self._manager.IndexToNode(from_index)
        return self._graph_exporter.export_priorities(self._match_input.graph)[from_node]
