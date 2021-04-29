from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.fleet.fleet_property_sets import BoardLevelProperties, DroneSetProperties
from common.entities.base_entities.zone import Zone
from experiment_space.experiment import Experiment
from experiment_space.graph_creation_algorithm import GraphCreationAlgorithm, create_graph_algorithm_by_name
from experiment_space.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig


@dataclass
class ImportedJsonParser(JsonableBaseEntity):
    delivery_requests_file_path: str
    drone_loading_docks_file_path: str
    zones_file_path: str
    drone_set_properties_list_path: str
    matcher_config_path: str
    graph_creation_algorithm: GraphCreationAlgorithm
    board_level_properties: BoardLevelProperties

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)

        graph_algorithm_name = dict_input['graph_creation_algorithm']['__class__']
        graph_algorithm_class = create_graph_algorithm_by_name(graph_algorithm_name)

        return ImportedJsonParser(
            delivery_requests_file_path=dict_input['delivery_requests_file_path'],
            drone_loading_docks_file_path=dict_input['drone_loading_docks_file_path'],
            zones_file_path=dict_input['zones_file_path'],
            drone_set_properties_list_path=dict_input['drone_set_properties_list_path'],
            matcher_config_path=dict_input['matcher_config_path'],
            graph_creation_algorithm=graph_algorithm_class.dict_to_obj(
                dict_input['graph_creation_algorithm']),
            board_level_properties=BoardLevelProperties.dict_to_obj(dict_input['board_level_properties'])
        )

    def save_as_experiment(self, file_path: Path):
        self.export_experiment().to_json(file_path=file_path)

    def export_experiment(self):
        return Experiment(supplier_category=self.export_supplier_category(),
                          drone_set_properties_list=self.export_drone_set_properties(),
                          matcher_config=self.export_matcher_config(),
                          graph_creation_algorithm=self.graph_creation_algorithm,
                          board_level_properties=self.board_level_properties)

    def export_supplier_category(self) -> SupplierCategory:
        delivery_requests_dict = DeliveryRequest.json_to_dict(Path(self.delivery_requests_file_path))
        drone_loading_docks_dict = DroneLoadingDock.json_to_dict(Path(self.drone_loading_docks_file_path))
        zones_dict = Zone.json_to_dict(Path(self.zones_file_path))

        return SupplierCategory(
            delivery_requests=[DeliveryRequest.dict_to_obj(dr_dict) for dr_dict in delivery_requests_dict],
            drone_loading_docks=[DroneLoadingDock.dict_to_obj(dld_dict)
                                 for dld_dict in drone_loading_docks_dict],
            zero_time=self.export_matcher_config().zero_time,
            zones=[Zone.dict_to_obj(zone_dict) for zone_dict in zones_dict])

    def export_drone_set_properties(self) -> List[DroneSetProperties]:
        drone_set_properties_dict = DroneSetProperties.json_to_dict(Path(self.drone_set_properties_list_path))
        return [DroneSetProperties.dict_to_obj(dsp_dict) for dsp_dict in
                drone_set_properties_dict]

    def export_matcher_config(self) -> MatcherConfig:
        matcher_config_dict = MatcherConfig.json_to_dict(Path(self.matcher_config_path))
        return MatcherConfig.dict_to_obj(matcher_config_dict)

    def __eq__(self, other):
        return self.delivery_requests_file_path == other.delivery_requests_file_path \
               and self.drone_loading_docks_file_path == other.drone_loading_docks_file_path \
               and self.zones_file_path == other.zones_file_path \
               and self.drone_set_properties_list_path == other.drone_set_properties_list_path \
               and self.matcher_config_path == other.matcher_config_path \
               and self.graph_creation_algorithm == other.graph_creation_algorithm \
               and self.board_level_properties == other.board_level_properties
