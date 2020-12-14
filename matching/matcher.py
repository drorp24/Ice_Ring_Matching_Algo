from abc import ABC, abstractmethod

from common.entities.drone_delivery_board import DroneDeliveryBoard
from matching.matcher_input import MatcherInput


class InvalidMatchInputException(Exception):
    pass


class Matcher(ABC):

    def __init__(self, matcher_input: MatcherInput):
        self._matcher_input = matcher_input

        self._validate_input()

    @property
    def matcher_input(self) -> MatcherInput:
        return self._matcher_input

    @abstractmethod
    def match(self) -> DroneDeliveryBoard:
        raise NotImplementedError()

    def _validate_input(self) -> bool:
        if self._matcher_input.empty_board.num_of_formations == 0:
            raise InvalidMatchInputException(f"Empty Board must has at least one formation")

        return True
