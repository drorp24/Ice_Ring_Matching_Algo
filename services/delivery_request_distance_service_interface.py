from abc import ABC

from common.entities.delivery_request import DeliveryRequest


class DeliveryRequestDistanceServiceInterface(ABC):

    @staticmethod
    def get_distance(delivery_request1: DeliveryRequest,delivery_request2: DeliveryRequest) -> float:
        raise NotImplementedError()
