from functools import lru_cache

from common.graph.operational.export_ortools_graph import OrtoolsGraphExporter
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_index_manager_wrapper import OrToolsIndexManagerWrapper


class ORToolsPriorityEvaluator:
    def __init__(self, index_manager: OrToolsIndexManagerWrapper,
                 matcher_input: MatcherInput, reloading_virtual_depos_indices: [int]):
        self._graph_exporter = OrtoolsGraphExporter()
        self._index_manager = index_manager
        self._matcher_input = matcher_input
        self._reloading_virtual_depos_indices = reloading_virtual_depos_indices
        self._num_of_nodes = len(self._matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)
        self._priorities = {}
        self.priority_evaluator = self.create_priority_evaluator()

    def create_priority_evaluator(self):

        def priority(_from_node):
            if _from_node in self._reloading_virtual_depos_indices:
                _from_node = self._graph_exporter.export_basis_nodes_indices(self._matcher_input.graph)[0]
            _priority = self._graph_exporter.export_priorities(self._matcher_input.graph)[_from_node] * \
                self._matcher_input.config.constraints.priority.priority_cost_coefficient
            return _priority

        _priorities = {}
        for from_node in range(self._num_of_nodes):
            _priorities[from_node] = int(priority(from_node))

        @lru_cache()
        def priority_evaluator(_from_index):
            return _priorities[self._index_manager.index_to_node(_from_index)]

        return priority_evaluator

