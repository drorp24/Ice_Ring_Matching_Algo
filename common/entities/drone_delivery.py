from datetime import datetime
from common.entities.delivery_request import DeliveryRequest
from common.entities.drone_formation import DroneFormation


class EmptyDroneDelivery:
    def __init__(self, id: str, drone_formation: DroneFormation):
        self._identity = id
        self._drone_formation = drone_formation

    @property
    def identity(self) -> str:
        return self._identity

    @property
    def drone_formation(self) -> DroneFormation:
        return self._drone_formation


class DroneDelivery(EmptyDroneDelivery):
    def __init__(self, id: str, drone_formation: DroneFormation, attack_time: datetime,
                 delivery_requests: [DeliveryRequest]):
        super().__init__(id, drone_formation)
        self._attack_time = attack_time
        self._delivery_requests = delivery_requests

    @property
    def attack_time(self) -> datetime:
        return self._attack_time

    @property
    def delivery_requests(self) -> [DeliveryRequest]:
        return self._delivery_requests
