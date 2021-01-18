from matching.matcher import Matcher
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher
from matching.solver_config import SolverVendor


def create_matcher(matcher_input: MatcherInput) -> Matcher:
    if matcher_input.config.solver.vendor == SolverVendor.OR_TOOLS:
        return ORToolsMatcher(matcher_input)
