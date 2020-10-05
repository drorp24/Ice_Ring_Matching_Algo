from datetime import datetime

from common.entities.delivery_request import DeliveryRequest
from common.entities.drone_formation import DroneFormationType


class EmptyDroneDelivery():
    def __init__(self, identity: str, drone_formation_type: DroneFormationType):
        self._identity = identity
        self._drone_formation_type = drone_formation_type

    @property
    def identity(self) -> str:
        return self._identity

    @property
    def drone_formation_type(self) -> DroneFormationType:
        return self._drone_formation_type


class DroneDelivery(EmptyDroneDelivery):
    def __init__(self, identity: str, drone_formation_type: DroneFormationType, attack_time: datetime,
                 delivery_requests: [DeliveryRequest]):
        super().__init__(identity, drone_formation_type)
        self._attack_time = attack_time
        self._delivery_requests = delivery_requests

    @property
    def attack_time(self) -> datetime:
        return self._attack_time

    @property
    def delivery_requests(self) -> [DeliveryRequest]:
        return self._delivery_requests
