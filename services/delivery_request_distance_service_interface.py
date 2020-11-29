from abc import ABC

from common.entities.delivery_request import DeliveryRequest


class DeliveryRequestDistanceServiceInterface(ABC):

    @staticmethod
    def get_distance_between_delivery_options(delivery_request1: DeliveryRequest, delivery_request2: DeliveryRequest,
                     delivery_request1_selected_option: int, delivery_request2_selected_option: int) -> float:
        raise NotImplementedError()
