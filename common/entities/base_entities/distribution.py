from __future__ import annotations
from abc import abstractmethod, ABC
from dataclasses import dataclass
from random import Random
from typing import Dict, List, Union, Tuple


class Distribution(ABC):

    @abstractmethod
    def choose_rand(self, random: Random):
        raise NotImplementedError


class ChoiceDistribution(Distribution):

    def __init__(self, options_to_probability: dict):
        ChoiceDistribution.validate_legal_probs(options_to_probability)
        self.options_to_prob = options_to_probability

    @staticmethod
    def get_safe_probabilities(probabilities: list):
        # if all probabilities are zero, use equal probabilities
        sum_probabilities = sum(probabilities)
        if sum_probabilities == 0:
            probabilities = [1.0 / probabilities.__len__()] * probabilities.__len__()
        else:
            probabilities = [prob / sum_probabilities for prob in probabilities]
        return probabilities

    def choose_rand(self, random: Random):
        values = list(self.options_to_prob.keys())
        probs = list(self.options_to_prob.values())
        return random.choices(values, ChoiceDistribution.get_safe_probabilities(probs))[0]

    def __str__(self):
        return str(self.options_to_prob)

    @staticmethod
    def validate_legal_probs(prob_dict: dict):
        if any([val < 0 for val in prob_dict.values()]):
            raise InvalidProbabilityException()


class UniformChoiceDistribution(Distribution):

    def __init__(self, values: Union[List, Tuple]):
        self._values = values

    def choose_rand(self, random: Random):
        return random.choice(self._values)


class UniformDistribution(Distribution):

    def __init__(self, value_range: Range):
        self._value_range = value_range

    def choose_rand(self, random: Random) -> float:
        # uniform sample from within range chosen by probability
        return random.uniform(self._value_range.start, self._value_range.stop)


class MultiUniformDistribution(Distribution):

    def __init__(self, range_to_probability: Dict):
        self._range_to_probability = range_to_probability

    def choose_rand(self, random: Random) -> float:
        # uniform sample from within range chosen by probability
        range_to_sample_from: Range = ChoiceDistribution(self._range_to_probability).choose_rand(random)
        return random.uniform(range_to_sample_from.start, range_to_sample_from.stop)


@dataclass
class Range:
    start: float
    stop: float

    def __hash__(self):
        return hash((self.start, self.stop))

    def __eq__(self, other: Range):
        return self.start == other.start and self.stop == other.stop


class InvalidProbabilityException(Exception):
    pass
