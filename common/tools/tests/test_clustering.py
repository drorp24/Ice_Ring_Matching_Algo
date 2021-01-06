import unittest

import numpy as np

from common.tools.clustering_alg import fit_k_means
from geometry.geo_factory import create_point_2d


class ClusteringTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        np.random.seed(0)
        dr_n = 400

        mu, sigma = 20, 5
        cls.data_set_1 = np.array(
            [(np.random.normal(mu, sigma), np.random.normal(mu, sigma)) for i in range(round(dr_n / 2))])

        mu, sigma = 30, 5
        cls.data_set_2 = np.array(
            [(np.random.normal(mu, sigma), np.random.normal(mu, sigma)) for i in range(round(dr_n / 2))])

    def test_k_means(self):
        all_data = np.concatenate((self.data_set_1, self.data_set_2), axis=0)

        best_fit = fit_k_means(data=all_data, max_clusters=10)

        expected_n_clusters = 2
        expected_0_labels = 197
        expected_1_labels = 203
        expected_centers = [(29.93, 29.63),
                            (19.34, 19.94)]

        best_fit_centers = [(round(center.x,2),round(center.y,2)) for center in best_fit.centers]

        self.assertEqual(expected_n_clusters, len(best_fit.centers))
        self.assertEqual(expected_centers, best_fit_centers)
        self.assertEqual(expected_0_labels, best_fit.labels.count(0))
        self.assertEqual(expected_1_labels, best_fit.labels.count(1))

        best_fit.plot(all_data)
