import uuid

from common.entities.base_entities.drone_delivery import EmptyDroneDelivery
from common.entities.base_entities.drone_delivery import DEFAULT_MAX_ROUTE_TIME_IN_MINUTES, \
    DEFAULT_VELOCITY_METER_PER_SEC
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.fleet_configuration_attribution import FleetConfigurationAttribution, \
    DroneFormationsPerTypeAmounts
from common.entities.base_entities.fleet.fleet_partition import FormationTypeAmounts, FleetPartition
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties


def _calc_formation_amounts(drone_set_properties: DroneSetProperties) -> FormationTypeAmounts:
    return FleetPartition(drone_set_properties).solve()


def _calc_drone_formation_amounts(formation_sizes_amounts: FormationTypeAmounts,
                                  drone_set_properties: DroneSetProperties) -> DroneFormationsPerTypeAmounts:
    FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, drone_set_properties)
    return FleetConfigurationAttribution.solve()


def calc_drone_deliveries(drone_set_properties: DroneSetProperties,
                          max_route_time_entire_board: int = DEFAULT_MAX_ROUTE_TIME_IN_MINUTES,
                          velocity_entire_board: float = DEFAULT_VELOCITY_METER_PER_SEC) -> [EmptyDroneDelivery]:
    empty_deliveries = []
    formation_type_amounts = _calc_formation_amounts(drone_set_properties)
    drone_formations_per_type_amounts = _calc_drone_formation_amounts(formation_type_amounts, drone_set_properties)
    for drone_formation, amount in drone_formations_per_type_amounts.amounts.items():
        for i in range(amount):
            empty_deliveries.append(EmptyDroneDelivery(EntityID(uuid.uuid4()), drone_formation,
                                                       max_route_time_entire_board, velocity_entire_board))
    return empty_deliveries


def generate_empty_delivery_board(drone_set_properties: [DroneSetProperties]) -> EmptyDroneDeliveryBoard:
    total_drone_deliveries = []
    for drone_properties in drone_set_properties:
        total_drone_deliveries += calc_drone_deliveries(drone_properties)
    return EmptyDroneDeliveryBoard(total_drone_deliveries)


def build_empty_drone_delivery_board(drone_set_properties: DroneSetProperties,
                                     max_route_time_entire_board: int,
                                     velocity_entire_board: float):
    return EmptyDroneDeliveryBoard(calc_drone_deliveries(drone_set_properties, max_route_time_entire_board,
                                                         velocity_entire_board))
