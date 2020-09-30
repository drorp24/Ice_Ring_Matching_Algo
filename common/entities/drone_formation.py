from __future__ import annotations

from common.entities.drone_model import DroneModel


class DroneFormation:
    def __init__(self, drone_model: DroneModel, quantity: int):
        self._drone_model = drone_model
        self._quantity = quantity

    @property
    def drone_model(self) -> [DroneModel]:
        return self._drone_model

    @property
    def quantity(self) -> int:
        return self._quantity
