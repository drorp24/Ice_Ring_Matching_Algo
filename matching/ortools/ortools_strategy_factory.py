from ortools.constraint_solver.routing_enums_pb2 import _FIRSTSOLUTIONSTRATEGY_VALUE, _LOCALSEARCHMETAHEURISTIC_VALUE


class ORToolsStrategyFactory(object):
    """The factory class """

    @staticmethod
    def create_first_solution_strategy(strategy):
        """A Static method to get a concrete object of type FirstSolutionStrategy"""
        strategy = str.upper(strategy.partition(':')[2])
        strategy = _FIRSTSOLUTIONSTRATEGY_VALUE.values_by_name.get(strategy)
        if strategy:
            return strategy.number
        raise AssertionError("FirstSolutionStrategy not found")

    @staticmethod
    def create_local_search_solver(solver):
        """A Static method to get a concrete object of type LocalSearchMetaheuristic"""
        solver = _LOCALSEARCHMETAHEURISTIC_VALUE.values_by_name.get(solver)
        if solver:
            return solver.number
        raise AssertionError("LocalSearchSolver not found")
