from abc import abstractmethod

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard


class Analyzer:

    @abstractmethod
    def calc_analysis(self, delivery_board: DroneDeliveryBoard):
        pass

    @property
    def name(self):
        pass


class QuantitativeAnalyzer(Analyzer):

    @abstractmethod
    def calc_analysis(self, delivery_board: DroneDeliveryBoard) -> float:
        pass
