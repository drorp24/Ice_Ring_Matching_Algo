from datetime import datetime

from attr import dataclass

from common.entities.delivery_request import DeliveryRequest
from common.entities.drone_formation import DroneFormation


class EmptyDroneDelivery:
    def __init__(self, id: str, drone_formation: DroneFormation):
        self._id = id
        self._drone_formation = drone_formation

    @property
    def id(self) -> str:
        return self._id

    @property
    def drone_formation(self) -> DroneFormation:
        return self._drone_formation


@dataclass
class MatchedDeliveryRequest:
    delivery_request: DeliveryRequest
    delivery_time: datetime


class DroneDelivery(EmptyDroneDelivery):
    def __init__(self, id: str, drone_formation: DroneFormation):
        super().__init__(id, drone_formation)
        self._matched_requests = []

    @property
    def matched_requests(self) -> [MatchedDeliveryRequest]:
        return self._matched_requests

    def add_matched_delivery_request(self, matched_request: MatchedDeliveryRequest) -> None:
        self._matched_requests.append(matched_request)

