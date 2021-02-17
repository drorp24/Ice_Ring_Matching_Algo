from abc import abstractmethod

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard


class Analyzer:

    @staticmethod
    @abstractmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard):
        pass

    @property
    @abstractmethod
    def name(self):
        pass


class QuantitativeAnalyzer(Analyzer):

    @staticmethod
    @abstractmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        pass
