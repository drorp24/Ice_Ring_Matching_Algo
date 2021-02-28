from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard
from experiment_space.analyzer.analyzer import Analyzer
from experiment_space.graph_creation_algorithm import GraphCreationAlgorithm
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


class Experiment(JsonableBaseEntity):

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
    def empty_drone_delivery_board(self):
        return self._empty_drone_delivery

    @property
    def matcher_config(self):
        return self._matcher_config

    @property
    def graph_creation_algorithm(self):
        return self._graph_creation_algorithm

    def run_match(self) -> DroneDeliveryBoard:
        graph = self._graph_creation_algorithm.create(supplier_category=self._supplier_category)
        matcher_input = MatcherInput(graph=graph, empty_board=self._empty_drone_delivery, config=self._matcher_config)
        delivery_board = create_matcher(matcher_input=matcher_input).match()
        return delivery_board

    @staticmethod
    def run_analysis_suite(droneDeliveryBoard: DroneDeliveryBoard, analyzers: [Analyzer]):
        return {analyzer.__name__: analyzer.calc_analysis(droneDeliveryBoard) for analyzer in analyzers}

    def __str__(self):
        return str((self._supplier_category, self._empty_drone_delivery, self._matcher_config))

    def __hash__(self):
        return hash((self._supplier_category, self._empty_drone_delivery, self._matcher_config))

    def __eq__(self, other):
        return self.supplier_category == other.supplier_category \
               and self.empty_drone_delivery_board == other.empty_drone_delivery_board \
               and self.matcher_config == other.matcher_config
