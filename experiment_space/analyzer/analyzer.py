from abc import abstractmethod, ABC

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard


class Analyzer(ABC):

    @staticmethod
    @abstractmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard):
        pass


class QuantitativeAnalyzer(Analyzer):

    @staticmethod
    @abstractmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        pass
