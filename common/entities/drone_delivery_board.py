from common.entities.drone_delivery import DroneDelivery, EmptyDroneDelivery


class EmptyDroneDeliveryBoard:
    def __init__(self, empty_drone_deliveries: [EmptyDroneDelivery]):
        self._empty_drone_deliveries = empty_drone_deliveries

    @property
    def empty_drone_deliveries(self) -> [EmptyDroneDelivery]:
        return self._empty_drone_deliveries


class DroneDeliveryBoard:
    def __init__(self, drone_deliveries: [DroneDelivery]):
        self._drone_deliveries = drone_deliveries

    @property
    def drone_deliveries(self) -> [DroneDelivery]:
        return self._drone_deliveries
