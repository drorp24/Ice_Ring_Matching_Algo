import unittest
from random import Random

import numpy as np

from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_distribution.priority_distribution import PriorityDistribution
from common.entities.distribution.distribution import Range
from common.entities.generator.delivery_request_generator import DeliveryRequestDatasetStructure, \
    DeliveryRequestDatasetGenerator
from common.tools.clustering_alg import fit_k_means
from geometry.distribution.geo_distribution import MultiNormalPointDistribution
from geometry.geo_factory import create_point_2d


class ClusteringDeliveryRequestsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.num_of_drs = 1000
        cls.num_of_do_per_dr = 1
        cls.num_of_cd_per_do = 1
        cls.num_of_pdp_per_cd = 1

        cls.center_points = [create_point_2d(20, 20), create_point_2d(80, 80)]

        dr_distribution = build_delivery_request_distribution(
            priority_distribution=PriorityDistribution([1, 2, 3, 4, 5]),
            relative_dr_location_distribution=MultiNormalPointDistribution(center_points=cls.center_points,
                                                                           sigma_x_range=Range(0, 15),
                                                                           sigma_y_range=Range(0, 15)))

        cls.ds = DeliveryRequestDatasetStructure(
            num_of_delivery_requests=cls.num_of_drs,
            num_of_delivery_options_per_delivery_request=cls.num_of_do_per_dr,
            num_of_customer_deliveries_per_delivery_option=cls.num_of_cd_per_do,
            num_of_package_delivery_plan_per_customer_delivery=cls.num_of_pdp_per_cd,
            delivery_request_distribution=dr_distribution)

        cls.random = Random()
        cls.random.seed(0)
        cls.dr_dataset = DeliveryRequestDatasetGenerator.generate(dr_struct=cls.ds,
                                                                  random=cls.random)

    def test_k_means(self):
        all_data = np.array(
            [[np.array(dr.calc_location().x), np.array(dr.calc_location().y)] for dr in self.dr_dataset])

        best_fit = fit_k_means(data=all_data, max_clusters=10)
        expected_n_clusters = 2
        expected_0_labels = self.num_of_drs / 2
        expected_1_labels = self.num_of_drs / 2

        self.assertEqual(expected_n_clusters, len(best_fit.centers))
        self.assertEqual(expected_0_labels, best_fit.labels.count(0))
        self.assertEqual(expected_1_labels, best_fit.labels.count(1))
