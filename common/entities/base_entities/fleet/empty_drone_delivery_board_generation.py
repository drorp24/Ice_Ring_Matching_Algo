import uuid


from common.entities.base_entities.drone_delivery import EmptyDroneDelivery
from common.entities.base_entities.drone_delivery_board import EmptyDroneDeliveryBoard
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.fleet_configuration_attribution import FleetConfigurationAttribution, \
    DroneFormationsPerTypeAmounts
from common.entities.base_entities.fleet.fleet_partition import FormationTypeAmounts, FleetPartition
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties


def _calc_formation_amounts(platform_property_set: DroneSetProperties) -> FormationTypeAmounts:
    return FleetPartition(platform_property_set).solve()


def _calc_drone_formation_amounts(formation_sizes_amounts: FormationTypeAmounts,
                                  platform_properties: DroneSetProperties) -> DroneFormationsPerTypeAmounts:
    FleetConfigurationAttribution.extract_parameters(formation_sizes_amounts, platform_properties)
    return FleetConfigurationAttribution.solve()


def calc_drone_deliveries(platform_properties: DroneSetProperties) -> [EmptyDroneDelivery]:
    empty_deliveries = []
    formation_type_amounts = _calc_formation_amounts(platform_properties)
    drone_formations_per_type_amounts = _calc_drone_formation_amounts(formation_type_amounts, platform_properties)
    for drone_formation, amount in drone_formations_per_type_amounts.amounts.items():
        for i in range(amount):
            empty_deliveries.append(EmptyDroneDelivery(EntityID(uuid.uuid4()), drone_formation))
    return empty_deliveries


def generate_empty_delivery_board(drone_set_properties: [DroneSetProperties]) -> EmptyDroneDeliveryBoard:
    total_drone_deliveries = []
    for drone_properties in drone_set_properties:
        total_drone_deliveries += calc_drone_deliveries(drone_properties)
    return EmptyDroneDeliveryBoard(total_drone_deliveries)


def build_empty_drone_delivery_board(drone_set_properties: DroneSetProperties):
    return EmptyDroneDeliveryBoard(calc_drone_deliveries(drone_set_properties))
