from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from experiment_space.analyzer.analyzer import QuantitativeAnalyzer


class UnmatchedDeliveryRequestsAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        return len(delivery_board.unmatched_delivery_requests)

    @property
    def name(self):
        return 'unmatched_delivery_requests'


class MatchedDeliveryRequestsAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        return MatchedDeliveryRequestsAnalyzer._calc_amount_matched_delivery_request(delivery_board)

    @staticmethod
    def _calc_amount_matched_delivery_request(delivery_board):
        return sum(list(map(lambda delivery: len(delivery.matched_requests), list(delivery_board.drone_deliveries))))

    @property
    def name(self):
        return 'matched_delivery_requests'


class MatchPercentageDeliveryRequestAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        unmatched_amount = UnmatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        matched_amount = MatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        return matched_amount / (unmatched_amount + matched_amount)

    @property
    def name(self):
        return 'matched_percentage_delivery_requests'
