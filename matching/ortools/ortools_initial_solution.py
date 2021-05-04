from matching.initial_solution import InitialSolution, Routes
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


class ORToolsInitialSolution(InitialSolution):

    def __init__(self, matcher_input: MatcherInput):
        super().__init__(matcher_input)
        self.matcher = create_matcher(matcher_input)

    def calc(self) -> Routes:
        return self.matcher.match_to_routes()
