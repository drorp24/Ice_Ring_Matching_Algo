from __future__ import annotations

from pathlib import Path

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.base_entities.fleet.delivering_drones_board_generation import generate_delivering_drones_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, BoardLevelProperties
from experiment_space.analyzer.analyzer import Analyzer
from experiment_space.graph_creation_algorithm import GraphCreationAlgorithm, List, create_graph_algorithm_by_name
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig
from matching.matcher_input import MatcherInput
from matching.matching_master import MatchingMaster


class Experiment(JsonableBaseEntity):

    def __init__(self, supplier_category: SupplierCategory,
                 drone_set_properties_list: [DroneSetProperties],
                 matcher_config: MatcherConfig,
                 graph_creation_algorithm: GraphCreationAlgorithm,
                 board_level_properties: BoardLevelProperties = BoardLevelProperties()):
        self._supplier_category = supplier_category
        self._drone_set_properties_list = drone_set_properties_list
        self._matcher_config = matcher_config
        self._graph_creation_algorithm = graph_creation_algorithm
        self._board_level_properties = board_level_properties

    @property
    def supplier_category(self):
        return self._supplier_category

    @property
    def drone_set_properties_list(self):
        return self._drone_set_properties_list

    @property
    def matcher_config(self):
        return self._matcher_config

    @property
    def graph_creation_algorithm(self):
        return self._graph_creation_algorithm

    @property
    def board_level_properties(self):
        return self._board_level_properties

    @classmethod
    def dict_to_obj(cls, dict_input):
        graph_algorithm_name = dict_input['graph_creation_algorithm']['__class__']
        graph_algorithm_class = create_graph_algorithm_by_name(graph_algorithm_name)
        return Experiment(supplier_category=SupplierCategory.dict_to_obj(dict_input['supplier_category']),
                          drone_set_properties_list=[DroneSetProperties.dict_to_obj(set_dict)
                                                     for set_dict in dict_input['drone_set_properties_list']],
                          matcher_config=MatcherConfig.dict_to_obj(dict_input['matcher_config']),
                          graph_creation_algorithm=graph_algorithm_class.dict_to_obj(
                              dict_input['graph_creation_algorithm']),
                          board_level_properties=BoardLevelProperties.dict_to_obj(dict_input['board_level_properties']))

    def run_match(self, graph=None, init_guess_path: Path = None) -> DroneDeliveryBoard:
        if graph is None:
            graph = self.graph_creation_algorithm.create(supplier_category=self.supplier_category)
        delivering_drones_board = generate_delivering_drones_board(self.drone_set_properties_list,
                                                                   self.board_level_properties)
        matcher_input = MatcherInput(graph=graph, delivering_drones_board=delivering_drones_board,
                                     config=self.matcher_config)
        delivery_board = MatchingMaster(
            matcher_input=matcher_input).match()
        return delivery_board

    @staticmethod
    def run_analysis_suite(drone_delivery_board: DroneDeliveryBoard, analyzers: [Analyzer]):
        return {analyzer.__name__: analyzer.calc_analysis(drone_delivery_board) for analyzer in analyzers}

    @staticmethod
    def run_multi_match_analysis_pipeline(experiments: List[Experiment], analyzers: [Analyzer]):
        return [(e, Experiment.run_analysis_suite(e.run_match(), analyzers)) for e in experiments]

    def __str__(self):
        return str((self.supplier_category, self.drone_set_properties_list, self.matcher_config,
                    self.graph_creation_algorithm, self.board_level_properties))

    def __hash__(self):
        return hash((self.supplier_category, self.drone_set_properties_list, self.matcher_config,
                     self.graph_creation_algorithm, self.board_level_properties))

    def __eq__(self, other):
        return (self.supplier_category == other.supplier_category) \
               and (self.drone_set_properties_list == other.drone_set_properties_list) \
               and (self.matcher_config == other.matcher_config) \
               and (self.graph_creation_algorithm == other.graph_creation_algorithm) \
               and (self.board_level_properties == other.board_level_properties)
