from itertools import product
from itertools import product
from random import Random
from typing import List

from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard
from common.entities.base_entities.entity_distribution.distribution_utils import choose_rand_from_list_by_attrib
from experiment_space.analyzer.analyzer import Analyzer
from experiment_space.supplier_category import SupplierCategory
from experiment_space.graph_creation_algorithm import GraphCreationAlgorithm
from matching.matcher_config import MatcherConfig
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


class Experiment:

    def __init__(self, supplier_category: SupplierCategory,
                 empty_drone_delivery_board: EmptyDroneDeliveryBoard,
                 matcher_config: MatcherConfig,
                 graph_creation_algorithm: GraphCreationAlgorithm):
        self._supplier_category = supplier_category
        self._empty_drone_delivery = empty_drone_delivery_board
        self._matcher_config = matcher_config
        self._graph_creation_algorithm = graph_creation_algorithm

    @property
    def supplier_category(self):
        return self._supplier_category

    @property
    def empty_drone_delivery(self):
        return self._empty_drone_delivery

    @property
    def matcher_config(self):
        return self._matcher_config

    def run_match(self) -> DroneDeliveryBoard:
        graph = self._graph_creation_algorithm.create(supplier_category=self._supplier_category)
        matcher_input = MatcherInput(graph=graph, empty_board=self._empty_drone_delivery, config=self._matcher_config)
        delivery_board = create_matcher(matcher_input=matcher_input).match()
        return delivery_board

    @staticmethod
    def run_analysis_suite(droneDeliveryBoard: DroneDeliveryBoard, analyzers: [Analyzer]):
        return {analyzer.name: analyzer.calc_analysis(droneDeliveryBoard) for analyzer in analyzers}

    def __str__(self):
        return str((self._supplier_category, self._empty_drone_delivery, self._matcher_config))

    def __hash__(self):
        return hash((self._supplier_category, self._empty_drone_delivery, self._matcher_config))

    def __eq__(self, other):
        return self.supplier_category == other.supplier_category \
               and self.empty_drone_delivery == other.empty_drone_delivery \
               and self.matcher_config == other.matcher_config


class MultiExperiment:

    def __init__(self, supplier_categories: [SupplierCategory],
                 empty_drone_delivery_boards: [EmptyDroneDeliveryBoard],
                 matcher_configs: [MatcherConfig],
                 graph_creation_algorithms: [GraphCreationAlgorithm]):
        self._variations = {SupplierCategory: supplier_categories,
                            EmptyDroneDeliveryBoard: empty_drone_delivery_boards,
                            MatcherConfig: matcher_configs,
                            GraphCreationAlgorithm: graph_creation_algorithms}

    def calc_cartesian_product_experiments(self) -> List[Experiment]:
        variance = self._variations
        return [Experiment(e[0], e[1], e[2], e[3]) for e in
                product(variance[SupplierCategory], variance[EmptyDroneDeliveryBoard],
                        variance[MatcherConfig], variance[GraphCreationAlgorithm])]

    def calc_random_k_experiments(self, random: Random, amount: int) -> List[Experiment]:
        variation_samples = choose_rand_from_list_by_attrib(options_dict=self._variations, random=random, amount=amount)
        return [Experiment(e[0], e[1], e[2], e[3]) for e in
                zip(variation_samples[SupplierCategory], variation_samples[EmptyDroneDeliveryBoard],
                    variation_samples[MatcherConfig], variation_samples[GraphCreationAlgorithm])]
