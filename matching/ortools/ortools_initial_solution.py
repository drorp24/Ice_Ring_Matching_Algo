from matching.initial_solution import InitialSolution, Routes
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


class ORToolsInitialSolution(InitialSolution):

    @staticmethod
    def calc(matcher_input: MatcherInput) -> Routes:
        matcher = create_matcher(matcher_input)
        return matcher.match_to_routes()
