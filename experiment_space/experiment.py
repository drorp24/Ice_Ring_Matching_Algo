from __future__ import annotations

from pathlib import Path

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.base_entities.fleet.delivering_drones_board_generation import generate_delivering_drones_board
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties, BoardLevelProperties
from common.graph.operational.operational_graph import OperationalGraph
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
                 operational_graph_path: str = "",
                 delivery_board_path: str = "",
                 board_level_properties: BoardLevelProperties = BoardLevelProperties()):
        self._supplier_category = supplier_category
        self._drone_set_properties_list = drone_set_properties_list
        self._matcher_config = matcher_config
        self._graph_creation_algorithm = graph_creation_algorithm
        self._board_level_properties = board_level_properties
        self._operational_graph_path = operational_graph_path
        self._delivery_board_path = delivery_board_path

    @property
    def supplier_category(self) -> SupplierCategory:
        return self._supplier_category

    @property
    def drone_set_properties_list(self) -> DroneDeliveryBoard:
        return self._drone_set_properties_list

    @property
    def matcher_config(self) -> MatcherConfig:
        return self._matcher_config

    @property
    def graph_creation_algorithm(self) -> GraphCreationAlgorithm:
        return self._graph_creation_algorithm

    @property
    def board_level_properties(self) -> BoardLevelProperties:
        return self._board_level_properties

    @property
    def operational_graph_path(self) -> str:
        return self._operational_graph_path

    @property
    def delivery_board_path(self) -> str:
        return self._delivery_board_path

    @classmethod
    def dict_to_obj(cls, dict_input: dict):
        graph_algorithm_name = dict_input['graph_creation_algorithm']['__class__']
        graph_algorithm_class = create_graph_algorithm_by_name(graph_algorithm_name)
        return Experiment(supplier_category=SupplierCategory.dict_to_obj(dict_input['supplier_category']),
                          drone_set_properties_list=[DroneSetProperties.dict_to_obj(set_dict)
                                                     for set_dict in dict_input['drone_set_properties_list']],
                          matcher_config=MatcherConfig.dict_to_obj(dict_input['matcher_config']),
                          graph_creation_algorithm=graph_algorithm_class.dict_to_obj(
                              dict_input['graph_creation_algorithm']),
                          board_level_properties=BoardLevelProperties.dict_to_obj(dict_input['board_level_properties']),
                          operational_graph_path=dict_input['operational_graph_path'],
                          delivery_board_path=dict_input['delivery_board_path']
                          )

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

    def export_drone_delivery(self) -> DroneDeliveryBoard:
        return DroneDeliveryBoard.dict_to_obj(DroneDeliveryBoard.json_to_dict(Path(self.delivery_board_path)))

    def export_operational_graph(self) -> OperationalGraph:
        return OperationalGraph.dict_to_obj(OperationalGraph.json_to_dict(Path(self.operational_graph_path)))

    def __str__(self):
        return str((self.supplier_category, self.drone_set_properties_list, self.matcher_config,
                    self.graph_creation_algorithm, self.board_level_properties))

    def __hash__(self):
        return hash((self.supplier_category, self.drone_set_properties_list, self.matcher_config,
                     self.graph_creation_algorithm, self.board_level_properties, self.operational_graph_path,
                     self.delivery_board_path))

    def __eq__(self, other):
        return all([self.supplier_category == other.supplier_category,
                    self.drone_set_properties_list == other.drone_set_properties_list,
                    self.matcher_config == other.matcher_config,
                    self.graph_creation_algorithm == other.graph_creation_algorithm,
                    self.board_level_properties == other.board_level_properties,
                    self.delivery_board_path == other.delivery_board_path,
                    self.operational_graph_path == other.operational_graph_path])
