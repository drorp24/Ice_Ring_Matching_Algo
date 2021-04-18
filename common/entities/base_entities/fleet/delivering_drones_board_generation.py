import uuid

from common.entities.base_entities.drone_delivery import DeliveringDrones
from common.entities.base_entities.drone_delivery import DEFAULT_MAX_ROUTE_TIME_IN_MINUTES, \
    DEFAULT_VELOCITY_METER_PER_SEC
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard
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


def _calc_drone_deliveries(drone_set_properties: DroneSetProperties,
                           max_route_time_entire_board: int = DEFAULT_MAX_ROUTE_TIME_IN_MINUTES,
                           velocity_entire_board: float = DEFAULT_VELOCITY_METER_PER_SEC) -> [DeliveringDrones]:
    delivering_drones_list = []
    formation_type_amounts = _calc_formation_amounts(drone_set_properties)
    drone_formations_per_type_amounts = _calc_drone_formation_amounts(formation_type_amounts, drone_set_properties)
    for drone_formation, amount in drone_formations_per_type_amounts.amounts.items():
        for i in range(amount):
            delivering_drones_list.append(DeliveringDrones(id_=EntityID(uuid.uuid4()),
                                                     drone_formation=drone_formation,
                                                     start_loading_dock=drone_set_properties.start_loading_dock,
                                                     end_loading_dock=drone_set_properties.end_loading_dock,
                                                     max_route_time_in_minutes=max_route_time_entire_board,
                                                     velocity_meter_per_sec=velocity_entire_board))
    return delivering_drones_list


def generate_delivering_drones_board(drone_set_properties: [DroneSetProperties], max_route_time_entire_board: int,
                                  velocity_entire_board: float) -> DeliveringDronesBoard:
    total_drone_deliveries = []
    for drone_properties in drone_set_properties:
        total_drone_deliveries += _calc_drone_deliveries(drone_properties, max_route_time_entire_board,
                                                         velocity_entire_board)
    return DeliveringDronesBoard(total_drone_deliveries)


def build_delivering_drones_board(drone_set_properties: DroneSetProperties, max_route_time_entire_board: int,
                                     velocity_entire_board: float):
    return DeliveringDronesBoard(_calc_drone_deliveries(drone_set_properties, max_route_time_entire_board,
                                                        velocity_entire_board))
