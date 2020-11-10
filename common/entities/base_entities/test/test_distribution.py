import unittest
from collections import Counter
from random import Random
from typing import Union

from common.entities.base_entities.distribution import MultiUniformDistribution, Range, UniformChoiceDistribution


class BasicDistributionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.mud = MultiUniformDistribution({Range(0, 10): 0.1, Range(10, 15): 0.9})
        cls.ucd = UniformChoiceDistribution(list(range(0, 10)))

    def test_probability_of_package_generation_is_correct(self):
        rand_samples = 10000
        samples = list(map(lambda i: self.mud.choose_rand(Random()), range(rand_samples)))
        samples_in_range = list(map(lambda k: 0 < k < 10, samples))
        sample_prob = dict(Counter(samples_in_range))
        expected_prob = {0: 0.9, 1: 0.1}
        assert_samples_approx_expected(self, 0, expected_prob, sample_prob)

    def test_uniform_choice_distribution(self):
        samples = self.ucd.choose_rand(Random(5), 100)
        self.assertEqual(len(samples), 100)
        self.assertTrue(all([num in Counter(samples).keys() for num in list(range(0, 10))]))


def assert_samples_approx_expected(self, key: Union[str, int], expected_package_prob: dict, sample_count: dict,
                                   delta: float = 0.03):
    package_sample_prob = sample_count.get(key, 0) / sum(sample_count.values())
    self.assertAlmostEqual(first=package_sample_prob, second=expected_package_prob.get(key), delta=delta)
