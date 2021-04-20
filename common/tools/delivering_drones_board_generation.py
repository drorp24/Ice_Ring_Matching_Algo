from common.entities.base_entities.drone_delivery import DeliveringDrones
from common.entities.base_entities.drone_delivery import DEFAULT_MAX_ROUTE_TIME_IN_MINUTES, DEFAULT_VELOCITY_METER_PER_SEC
from common.entities.base_entities.drone_delivery_board import DeliveringDronesBoard
from common.entities.base_entities.entity_id import EntityID
from common.tools.fleet_property_sets import PlatformPropertySet
from common.tools.fleet_partition import FormationSizesAmounts, FleetPartition
from common.tools.fleet_configuration_attribution import DroneFormationsPerTypeAmounts, FleetConfigurationAttribution
from common.tools.fleet_reader import FleetReader
import uuid


def _calc_formation_amounts(platform_properties: PlatformPropertySet) -> FormationSizesAmounts:
    FleetPartition.extract_parameters(platform_properties)
    return FleetPartition.solve()


def _calc_drone_formation_amounts(formation_sizes_amounts: FormationSizesAmounts,
                                  platform_properties: PlatformPropertySet) -> DroneFormationsPerTypeAmounts:
    FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, platform_properties)
    return FleetConfigurationAttribution.solve()


def calc_drone_deliveries(platform_properties: PlatformPropertySet,
                          max_route_time_entire_board: int = DEFAULT_MAX_ROUTE_TIME_IN_MINUTES,
                          velocity_entire_board: float = DEFAULT_VELOCITY_METER_PER_SEC) -> [DeliveringDrones]:
    delivering_drones_list = []
    formation_sizes_amounts = _calc_formation_amounts(platform_properties)
    drone_formations_per_type_amounts = _calc_drone_formation_amounts(formation_sizes_amounts, platform_properties)
    for drone_formation, amount in drone_formations_per_type_amounts.amounts.items():
        for i in range(amount):
            delivering_drones_list.append(DeliveringDrones(EntityID(uuid.uuid4()), drone_formation,
                                                     max_route_time_entire_board, velocity_entire_board))
    return delivering_drones_list


def generate_delivering_drones_board(fleet_reader: FleetReader) -> DeliveringDronesBoard:
    platforms_properties = fleet_reader.get_platforms_properties()
    total_drone_deliveries = []
    for platform_property in platforms_properties:
        total_drone_deliveries += calc_drone_deliveries(platform_property)
    return DeliveringDronesBoard(total_drone_deliveries)


def build_delivering_drones_board(platform_properties: PlatformPropertySet, max_route_time_entire_board: int,
                                     velocity_entire_board: float):
    return DeliveringDronesBoard(calc_drone_deliveries(platform_properties, max_route_time_entire_board,
                                   velocity_entire_board))