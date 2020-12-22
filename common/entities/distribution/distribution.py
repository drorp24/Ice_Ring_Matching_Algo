from __future__ import annotations

from abc import abstractmethod, ABC, ABCMeta
from dataclasses import dataclass
from random import Random
from typing import Dict, List


class Distribution(ABC):

    @abstractmethod
    def choose_rand(self, random: Random, amount: int):
        raise NotImplementedError


class HierarchialDistribution(Distribution):

    @abstractmethod
    def choose_rand(self, random: Random, amount: Dict[type, int]):
        raise NotImplementedError


class ChoiceDistribution(Distribution):

    def __init__(self, options_to_probability: dict):
        ChoiceDistribution.validate_legal_probs(options_to_probability)
        self.options_to_prob = options_to_probability

    def get_choices(self) -> list:
        return list(self.options_to_prob.keys())

    @staticmethod
    def get_safe_probabilities(probabilities: list):
        # if all probabilities are zero, use equal probabilities
        probabilities = [max(prob, 0) for prob in probabilities]
        sum_probabilities = sum(probabilities)
        if sum_probabilities == 0:
            probabilities = [1.0 / probabilities.__len__()] * probabilities.__len__()
        else:
            probabilities = [prob / sum_probabilities for prob in probabilities]
        return probabilities

    def choose_rand(self, random: Random, amount=1):
        values = list(self.options_to_prob.keys())
        probs = list(self.options_to_prob.values())
        return random.choices(values, ChoiceDistribution.get_safe_probabilities(probs), k=amount)

    def __str__(self):
        return str(self.options_to_prob)

    @staticmethod
    def validate_legal_probs(prob_dict: dict):
        if any([val < 0 for val in prob_dict.values()]):
            raise InvalidProbabilityException()


class UniformChoiceDistribution(Distribution):

    def __init__(self, values: List):
        if not isinstance(values, list):
            values = [values]
        self._values = values

    def choose_rand(self, random: Random, amount: int = 1) -> List:
        return random.choices(self._values, k=amount)


class UniformDistribution(Distribution):

    def __init__(self, value_range: Range):
        self._value_range = value_range

    def choose_rand(self, random: Random, amount: int = 1) -> List:
        # uniform sample from within range chosen by probability
        return [random.uniform(self._value_range.start, self._value_range.stop) for _ in range(amount)]

    def choose_uniform_in_range(self, random: Random) -> object:
        # uniform sample from within range chosen by probability
        return random.uniform(self._value_range.start, self._value_range.stop)


class MultiUniformDistribution(Distribution):

    def __init__(self, range_to_probability: Dict):
        self._range_to_probability = range_to_probability

    def choose_rand(self, random: Random, amount: int = 1) -> List:
        # uniform sample from within range chosen by probability
        return [self.calc_value_within_range_based_on_prob(random) for i in range(amount)]

    def calc_value_within_range_based_on_prob(self, random):
        range_to_sample_from: Range = ChoiceDistribution(self._range_to_probability).choose_rand(random)[0]
        value_in_range = random.uniform(range_to_sample_from.start, range_to_sample_from.stop)
        return value_in_range


@dataclass
class Range:
    start: float
    stop: float

    def __hash__(self):
        return hash((self.start, self.stop))

    def __eq__(self, other: Range):
        return self.start == other.start and self.stop == other.stop

    def __contains__(self, item: float):
        return self.start <= item <= self.stop


class InvalidProbabilityException(Exception):
    pass
