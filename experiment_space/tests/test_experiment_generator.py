import unittest
from pathlib import Path
from random import Random

from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from experiment_space.experiment import Experiment
from experiment_space.experiment_generator import create_options_class, Options
from experiment_space.graph_creation_algorithm import FullyConnectedGraphAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


class BasicExperimentGeneratorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        supplier_category_path = Path('experiment_space/tests/jsons/test_supplier_category.json')
        supplier_category = SupplierCategory.from_json(SupplierCategory, supplier_category_path)
        matcher_config_path = Path('experiment_space/tests/jsons/test_matcher_config.json')
        matcher_config = MatcherConfig.from_json(MatcherConfig, matcher_config_path)
        drone_set_properties_path = Path('experiment_space/tests/jsons/test_drone_set_properties.json')
        drone_set_properties = DroneSetProperties.from_json(DroneSetProperties, drone_set_properties_path)
        default_graph_creation_algorithm = FullyConnectedGraphAlgorithm()
        cls.base_experiment = Experiment(supplier_category=supplier_category,
                                         matcher_config=matcher_config,
                                         drone_set_properties_list=[drone_set_properties],
                                         graph_creation_algorithm=default_graph_creation_algorithm)

    def test_experiment_generator_cartesian_samples_without_changes_maps_back_to_self(self):
        base_experiment_options = create_options_class(self.base_experiment, ['SupplierCategory', 'MatcherConfig'])
        sample = Options.calc_cartesian_product(base_experiment_options)
        self.assertEqual(sample[0], self.base_experiment)

    def test_experiment_generator_random_sample_without_changes_maps_back_to_self(self):
        base_experiment_options = create_options_class(self.base_experiment, ['SupplierCategory', 'MatcherConfig'])
        sample = Options.calc_random_k(base_experiment_options, amount=1, random=Random(42))
        self.assertEqual(sample[0], self.base_experiment)

    def test_experiment_generator_random_k_samples_without_changes_maps_back_to_self(self):
        base_experiment_options = create_options_class(self.base_experiment, ['SupplierCategory', 'MatcherConfig'])
        samples = Options.calc_random_k(base_experiment_options, amount=10, random=Random(42))
        for sample in samples:
            self.assertEqual(sample, self.base_experiment)

    def test_experiment_generator_cartesian_product_with_added_zones_and_unmatched_penalty(self):
        base_experiment_options = create_options_class(self.base_experiment, ['SupplierCategory', 'MatcherConfig'])
        base_experiment_options.supplier_category[0].zones.append('a')
        base_experiment_options.supplier_category[0].zones.append('b')
        base_experiment_options.matcher_config[0].unmatched_penalty.append(1000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(2000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(5000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(10000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(50000)
        samples = Options.calc_cartesian_product(base_experiment_options)
        self.assertEqual(len(samples), len(base_experiment_options.supplier_category[0].zones) *
                         len(base_experiment_options.matcher_config[0].unmatched_penalty))

    def test_experiment_generator_random_sample_with_added_zones_and_unmatched_penalty(self):
        base_experiment_options = create_options_class(self.base_experiment, ['SupplierCategory', 'MatcherConfig'])
        base_experiment_options.supplier_category[0].zones.append('a')
        base_experiment_options.supplier_category[0].zones.append('b')
        base_experiment_options.matcher_config[0].unmatched_penalty.append(1000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(2000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(5000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(10000)
        base_experiment_options.matcher_config[0].unmatched_penalty.append(50000)
        samples = Options.calc_random_k(base_experiment_options, amount=50, random=Random(21))
        self.assertEqual(len(samples), 50)
