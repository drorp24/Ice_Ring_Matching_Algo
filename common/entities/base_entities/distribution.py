from random import Random


class ChoiceDistribution:
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


class InvalidProbabilityException(Exception):
    pass
