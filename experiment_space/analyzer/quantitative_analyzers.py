from itertools import chain
from typing import Dict

from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.base_entities.package import PackageType
from experiment_space.analyzer.analyzer import QuantitativeAnalyzer, Analyzer


class UnmatchedDeliveryRequestsAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        return UnmatchedDeliveryRequestsAnalyzer._calc_amount_of_unmatched_delivery_requests(delivery_board)

    @staticmethod
    def _calc_amount_of_unmatched_delivery_requests(delivery_board):
        return len(delivery_board.unmatched_delivery_requests)


class MatchedDeliveryRequestsAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        return MatchedDeliveryRequestsAnalyzer._calc_amount_of_matched_delivery_request(delivery_board)

    @staticmethod
    def _calc_amount_of_matched_delivery_request(delivery_board):
        return sum(list(map(lambda delivery: len(delivery.matched_requests), list(delivery_board.drone_deliveries))), 0)


class MatchPercentageDeliveryRequestAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        unmatched_amount = UnmatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        matched_amount = MatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        return matched_amount / max(unmatched_amount + matched_amount, 0.0001)


class TotalWorkTimeAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        return TotalWorkTimeAnalyzer._calc_total_work_time_in_minutes(delivery_board)

    @staticmethod
    def _calc_total_work_time_in_minutes(delivery_board: DroneDeliveryBoard) -> float:
        return sum([delivery.get_total_work_time_in_minutes() for delivery in delivery_board.drone_deliveries])


class AmountMatchedPerPackageTypeAnalyzer(Analyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> Dict:
        return AmountMatchedPerPackageTypeAnalyzer._calc_total_amount_matched_per_package_type(delivery_board)

    @staticmethod
    def _calc_total_amount_matched_per_package_type(delivery_board: DroneDeliveryBoard) -> Dict:
        amount_matched_per_package_type = PackageTypeAmountMap({package: 0 for package in PackageType})
        for drone_delivery in delivery_board.drone_deliveries:
            amount_matched_per_package_type.add_packages_to_map(drone_delivery.get_total_package_type_amount_map())
        return amount_matched_per_package_type.package_type_to_amounts


class MatchingEfficiencyAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        return MatchingEfficiencyAnalyzer._calc_match_efficiency_score(delivery_board)

    @staticmethod
    def _calc_match_efficiency_score(delivery_board: DroneDeliveryBoard) -> float:
        amount_unmatched = UnmatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        amount_matched = MatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        return 100.0 * (amount_matched / (amount_unmatched + amount_matched))


class MatchingPriorityEfficiencyAnalyzer(QuantitativeAnalyzer):

    @staticmethod
    def calc_analysis(delivery_board: DroneDeliveryBoard) -> float:
        return MatchingPriorityEfficiencyAnalyzer._calc_match_priority_efficiency_score(delivery_board)

    @staticmethod
    def _calc_match_priority_efficiency_score(delivery_board: DroneDeliveryBoard) -> float:
        num_unmatched = UnmatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        num_matched = MatchedDeliveryRequestsAnalyzer.calc_analysis(delivery_board)
        unmatched_priorities = list(map(lambda dr: dr.delivery_request.priority,
                                        list(delivery_board.unmatched_delivery_requests)))
        matched_priorities = list(map(lambda mr: mr.delivery_request.priority, list(chain.from_iterable(
            map(lambda dr: dr.matched_requests, list(delivery_board.drone_deliveries))))))
        all_priorities = unmatched_priorities + matched_priorities
        priority_eff = 100.0 * (1 - (max(all_priorities) * num_unmatched - sum(unmatched_priorities)) /
                                (max(all_priorities) * (num_matched + num_unmatched) - sum(all_priorities)))
        return priority_eff
