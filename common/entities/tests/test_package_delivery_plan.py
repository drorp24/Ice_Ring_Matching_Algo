import json
import unittest
from pprint import pprint
from random import Random

from common.entities.customer_delivery import DEFAULT_PDP_DISTRIB


class BasicPDPTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.package_delivery_distrib = DEFAULT_PDP_DISTRIB

    def test_random_generation_of_package_delivery_plans(self):
        num_instances = 10
        samples_from_distribution = self.package_delivery_distrib.choose_rand(Random(), num_instances)
        self.assertEqual(len(samples_from_distribution), num_instances)
        unique_samples = len(set(samples_from_distribution * 5))
        self.assertEqual(unique_samples, num_instances)

    def test_random_generation_is_reproducible(self):
        samples_from_distribution1 = self.package_delivery_distrib.choose_rand(Random(100), 100)
        samples_from_distribution2 = self.package_delivery_distrib.choose_rand(Random(100), 100)
        self.assertEqual(samples_from_distribution1, samples_from_distribution2)

        samples_from_distribution3 = self.package_delivery_distrib.choose_rand(Random(103), 100)
        self.assertNotEqual(samples_from_distribution1, samples_from_distribution3)

    def print_example_of_package_delivery(self):
        pprint(self.package_delivery_distrib.choose_rand(Random(100), 1)[0].__dict__())
