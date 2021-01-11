from dataclasses import dataclass
from typing import List

import numpy as np
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn.base import ClusterMixin
from sklearn.cluster import KMeans
from sklearn.model_selection import GridSearchCV

from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d


@dataclass
class BestFit:
    labels: List[int]
    centers: List[Point2D]

    @classmethod
    def create_best_fit(cls, labels: np.ndarray, centers: np.ndarray):
        return cls(list(labels), [create_point_2d(center[0], center[1]) for center in centers])

    def plot(self, data: np.ndarray):
        fig, ax = plt.subplots()

        for i in np.unique(self.labels):
            ax.scatter(data[self.labels == i, 0], data[self.labels == i, 1], s=20, label=i)

        centers = np.array([[np.array(point.x), np.array(point.y)] for point in self.centers])
        ax.scatter(centers[:, 0], centers[:, 1], s=40, color='k', label='Centroids')
        plt.show()


def _silhouette_score(estimator: ClusterMixin, data: np.ndarray):
    labels = estimator.fit_predict(data)
    try:
        score = metrics.silhouette_score(data, labels, metric='euclidean')
    except ValueError:
        score = -1
    return score


def fit_k_means(data: np.ndarray, max_clusters: int) -> BestFit:
    k_means_estimator = KMeans(random_state=0)
    params_grid = {'n_clusters': list(range(1, max_clusters))}
    grid_search = GridSearchCV(k_means_estimator, params_grid, scoring=_silhouette_score,
                               cv=[(slice(None), slice(None))],
                               error_score=-1)
    grid_search.fit(data)

    return BestFit.create_best_fit(grid_search.best_estimator_.labels_,
                                   grid_search.best_estimator_.cluster_centers_)
