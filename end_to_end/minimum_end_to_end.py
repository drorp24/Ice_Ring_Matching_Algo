from dataclasses import dataclass
from pathlib import Path

from common.entities.base_entity import JsonableBaseEntity
from common.entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard
from common.graph.operational.graph_creator import *
from end_to_end.scenario import Scenario
from common.tools.empty_drone_delivery_board_generation import generate_empty_delivery_board, FleetReader
from matching.matcher import MatchInput, MatchConfig
from matching.ortools.ortools_matcher import ORToolsMatcher
from common.entities.temporal import DateTimeExtension


class MinimumEnd2EndConfig(JsonableBaseEntity):
    def __init__(self, scenario_json: Path, fleet_partition_json: Path, matcher_config_path: Path):
        self._scenario_json = scenario_json
        self._fleet_partition_json = fleet_partition_json
        self._matcher_config_json = matcher_config_path

    @classmethod
    def dict_to_obj(cls, dict_input):
        return MinimumEnd2EndConfig(Path(dict_input['scenario_json']),
                                    Path(dict_input['fleet_partition_json']),
                                    Path(dict_input['matcher_config_json']))

    @property
    def scenario_json(self) -> Path:
        return self._scenario_json

    @property
    def fleet_partition_json(self) -> Path:
        return self._fleet_partition_json

    @property
    def matcher_config_json(self) -> Path:
        return self._matcher_config_json

    @scenario_json.getter
    def scenario_json(self) -> str:
        return str(self._scenario_json)

    @fleet_partition_json.getter
    def fleet_partition_json(self) -> str:
        return str(self._fleet_partition_json)

    @matcher_config_json.getter
    def matcher_config_json(self) -> str:
        return str(self._matcher_config_json)

    @scenario_json.setter
    def scenario_json(self, scenario_json: str):
        self._scenario_json = Path(scenario_json)

    @fleet_partition_json.setter
    def fleet_partition_json(self, fleet_partition_json: str):
        self._fleet_partition_json = Path(fleet_partition_json)

    @matcher_config_json.setter
    def matcher_config_json(self, matcher_config_json: str):
        self._matcher_config_json = Path(matcher_config_json)


class DataLoader:
    def __init__(self, config: MinimumEnd2EndConfig):
        self.scenario_dict = Scenario.json_to_dict(config.scenario_json)
        self.fleet_json = config.fleet_partition_json
        self.matcher_config_json = config.matcher_config_json

    def get_delivery_requests(self) -> List[DeliveryRequest]:
        scenario = Scenario.dict_to_obj(self.scenario_dict)
        return scenario.delivery_requests

    def get_docks(self) -> List[DroneLoadingDock]:
        scenario = Scenario.dict_to_obj(self.scenario_dict)
        return scenario.drone_loading_docks

    def get_empty_drone_delivery_board(self) -> EmptyDroneDeliveryBoard:
        fleet_reader = FleetReader(self.fleet_json)
        return generate_empty_delivery_board(fleet_reader)

    def get_zero_time(self) -> DateTimeExtension:
        scenario = Scenario.dict_to_obj(self.scenario_dict)
        return scenario.zero_time


class MinimumEnd2End:
    def __init__(self, data_loader: DataLoader):
        self.delivery_requests = data_loader.get_delivery_requests()
        self.loading_dock = data_loader.get_docks()
        self.empty_drone_delivery_board = data_loader.get_empty_drone_delivery_board()
        self.zero_time = data_loader.get_zero_time()

    def create_graph_model(self, max_cost_to_connect: float) -> OperationalGraph:
        operational_graph = OperationalGraph(self.zero_time.get_internal())
        operational_graph.add_drone_loading_docks(self.loading_dock)
        operational_graph.add_delivery_requests(self.delivery_requests)
        build_fully_connected_graph(operational_graph)
        #add_locally_connected_dr_graph(operational_graph, self.delivery_requests, max_cost_to_connect)
        #add_fully_connected_loading_docks(operational_graph, self.loading_dock)
        return operational_graph

    def calc_assignment(self, graph: OperationalGraph, match_config_file: Path) -> DroneDeliveryBoard:
        match_config_dict = MatchConfig.json_to_dict(match_config_file)
        match_input = MatchInput(graph, self.empty_drone_delivery_board, MatchConfig.dict_to_obj(match_config_dict))
        matcher = ORToolsMatcher(match_input)
        solution = matcher.match()
        solution.print_solution()
        return solution.delivery_board()
