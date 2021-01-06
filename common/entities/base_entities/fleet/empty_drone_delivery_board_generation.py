import uuid

from common.entities.base_entities.drone_delivery import EmptyDroneDelivery
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.fleet.fleet_configuration_attribution import DroneFormationsPerTypeAmounts, FleetConfigurationAttribution
from common.entities.base_entities.fleet.fleet_partition import FormationTypeAmounts, FleetPartition
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties


def _calc_formation_amounts(platform_properties: DroneSetProperties) -> FormationTypeAmounts:
    FleetPartition.extract_parameters(platform_properties)
    return FleetPartition.solve()


def _calc_drone_formation_amounts(formation_sizes_amounts: FormationTypeAmounts,
                                  platform_properties: DroneSetProperties) -> DroneFormationsPerTypeAmounts:
    FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, platform_properties)
    return FleetConfigurationAttribution.solve()


def calc_drone_deliveries(platform_properties: DroneSetProperties) -> [EmptyDroneDelivery]:
    empty_deliveries = []
    formation_sizes_amounts = _calc_formation_amounts(platform_properties)
    drone_formations_per_type_amounts = _calc_drone_formation_amounts(formation_sizes_amounts, platform_properties)
    for drone_formation, amount in drone_formations_per_type_amounts.amounts.items():
        for i in range(amount):
            empty_deliveries.append(EmptyDroneDelivery(str(uuid.uuid4()), drone_formation))
    return empty_deliveries


def generate_empty_delivery_board(platforms_properties: [DroneSetProperties]) -> EmptyDroneDeliveryBoard:
    total_drone_deliveries = []
    for platform_property in platforms_properties:
        total_drone_deliveries += calc_drone_deliveries(platform_property)
    return EmptyDroneDeliveryBoard(total_drone_deliveries)
