import matplotlib.pyplot as plt
import pandas as pd

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.drone_delivery import DeliveringDrones
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, DeliveringDronesBoard
from common.entities.base_entities.package import PackageType
from matching.matcher_config import MatcherConfig


def fleet_usage(matcher_config: MatcherConfig, delivery_requests: [DeliveryRequest], board: DroneDeliveryBoard):
    delivering_drones_board = DeliveringDronesBoard(
        list(set(delivery.delivering_drones for delivery in board.drone_deliveries)))

    potenial_package_type_amounts_dict = get_potenial_package_type_amounts(
        delivering_drones_board.delivering_drones_list,
        matcher_config.reload_per_vehicle)

    delivery_requests_package_type_amounts = get_delivery_requests_package_type_amounts(delivery_requests)

    matched_delivery_requests_package_type_amounts = board.get_total_amount_per_package_type()

    df_dr = pd.DataFrame(delivery_requests_package_type_amounts.repr_as_lists(), columns=['package_types', 'amounts'])
    df_dr.set_index('package_types', inplace=True)
    df_dr.rename(columns={"amounts": "requested"}, inplace=True)

    df_potential = pd.DataFrame(potenial_package_type_amounts_dict.repr_as_lists(),
                                columns=['package_types', 'amounts'])
    df_potential = df_dr.join(df_potential.set_index('package_types'), on='package_types')
    df_potential.rename(columns={"amounts": "potential"}, inplace=True)

    df_matched = pd.DataFrame(matched_delivery_requests_package_type_amounts.repr_as_lists(),
                              columns=['package_types', 'amounts'])
    df_matched = df_potential.join(df_matched.set_index('package_types'), on='package_types')
    df_matched.rename(columns={"amounts": "matched"}, inplace=True)

    fig, ax = plt.subplots()
    table = ax.table(cellText=df_matched.values, rowLabels=df_matched.index, cellLoc='center',
                     colColours=['gainsboro'] * len(df_matched), colLabels=df_matched.columns, loc='center',
                     colWidths=[0.25] * (len(df_matched.columns)))
    table.set_fontsize(14)
    table.scale(1, 4)
    ax.axis('off')

    plt.show()


def get_potenial_package_type_amounts(delivering_drones_list: [DeliveringDrones],
                                      reload_per_vehicle: int) -> PackageTypeAmountMap:
    return PackageTypeAmountMap({package_type: sum(
        list(map(lambda drone_delivery: drone_delivery.drone_formation.get_package_type_amount(
            package_type=package_type) * reload_per_vehicle,
                 delivering_drones_list))) for package_type in PackageType})


def get_delivery_requests_package_type_amounts(delivery_requests: [DeliveryRequest]) -> PackageTypeAmountMap:
    return PackageTypeAmountMap({package_type: sum(
        list(map(lambda delivery_request: delivery_request.delivery_options[0].get_package_type_amount(
            package_type=package_type),
                 delivery_requests))) for package_type in PackageType})
