from common.entities.drone_delivery import DroneDelivery, EmptyDroneDelivery


class EmptyDroneDeliveryBoard:
    def __init__(self, empty_drone_deliveries: [EmptyDroneDelivery]):
        self._empty_drone_deliveries = empty_drone_deliveries

    @property
    def empty_drone_deliveries(self) -> [EmptyDroneDelivery]:
        return self._empty_drone_deliveries

    @property
    def num_of_formations(self) -> [int]:
        return len(self._empty_drone_deliveries)

    @property
    def formation_capacities(self) -> [int]:
        capacities = []
        for delivery in self._empty_drone_deliveries:
            formation_volumes = delivery.drone_formation.get_package_type_volumes()
            capacities.append(formation_volumes[0])
        return capacities


class DroneDeliveryBoard:
    def __init__(self, drone_deliveries: [DroneDelivery]):
        self._drone_deliveries = drone_deliveries

    def __eq__(self, other):
        return self._drone_deliveries == other.drone_deliveries

    @property
    def drone_deliveries(self) -> [DroneDelivery]:
        return self._drone_deliveries

    def __str__(self):
        s = ""
        for dd in self._drone_deliveries:
            for mr in dd.matched_requests:
                s += "["+ str(mr.delivery_request.priority) + "] "
        return s
