from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard, DroneDeliveryBoard
from experiment.supplier_category_graph_creator import create_fully_connected_graph_model
from experiment.supplier_category import SupplierCategory
from matching.matcher_config import MatcherConfig
from matching.matcher_factory import create_matcher
from matching.matcher_input import MatcherInput


class Experiment:

    def __init__(self, supplier_category: SupplierCategory, empty_drone_delivery: EmptyDroneDeliveryBoard,
                 matcher_config: MatcherConfig):
        self._supplier_category = supplier_category
        self._empty_drone_delivery = empty_drone_delivery
        self._matcher_config = matcher_config

    def run_experiment(self) -> DroneDeliveryBoard:
        graph = create_fully_connected_graph_model(supplier_category=self._supplier_category)
        matcher_input = MatcherInput(graph=graph, empty_board=self._empty_drone_delivery, config=self._matcher_config)
        delivery_board = create_matcher(matcher_input=matcher_input).match()
        return delivery_board
