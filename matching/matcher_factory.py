from matching.matcher import Matcher
from matching.matcher_input import MatcherInput
from matching.ortools.ortools_matcher import ORToolsMatcher


def build_matcher(matcher_input: MatcherInput) -> Matcher:
    return ORToolsMatcher(matcher_input)
