from ortools.constraint_solver.pywrapcp import RoutingModel

from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher_constraints import OrToolsDimensionDescription
from matching.ortools.ortools_priority_evaluator import ORToolsPriorityEvaluator


class ORToolsMatcherObjective:
    def __init__(self, routing_model: RoutingModel, matcher_input: MatcherInput,
                 priority_evaluator:ORToolsPriorityEvaluator):
        self._routing_model = routing_model
        self._matcher_input = matcher_input
        self._priority_evaluator = priority_evaluator

    def add_priority(self):
        priority_callback_index = self._routing_model.RegisterUnaryTransitCallback(self._priority_evaluator.priority_evaluator)
        self._routing_model.SetArcCostEvaluatorOfAllVehicles(priority_callback_index)
        self._routing_model.AddDimension(
            priority_callback_index,
            0,
            self._matcher_input.config.constraints.priority.priority_cost_coefficient * 10000,
            True,
            OrToolsDimensionDescription.priority.value)