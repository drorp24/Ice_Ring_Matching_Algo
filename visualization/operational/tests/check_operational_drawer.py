from random import Random
from typing import List

from common.entities.delivery_request import build_delivery_request_distribution, DeliveryRequest
from common.entities.delivery_request_generator import DeliveryRequestDatasetStructure, DeliveryRequestDatasetGenerator
from common.entities.disribution.distribution import Range
from common.entities.drone_loading_dock import DroneLoadingDock, DroneLoadingDockDistribution
from common.graph.operational import graph_creator
from common.graph.operational.operational_graph import OperationalGraph
from geometry.geo_distribution import ChoiceNormalDistribution
from geometry.geo_factory import create_point_2d
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.operational.operational_drawer2d import add_delivery_request, add_operational_graph


def _create_dr_locations():
    dr_centers = [create_point_2d(4000, 500),
                  create_point_2d(0, -6000),
                  create_point_2d(-5000, 450),
                  create_point_2d(-6000, 2000),
                  create_point_2d(4200, 1900),
                  create_point_2d(5000, 300)]
    dr_sig_x = dr_sig_y = Range(100, 100)
    return dr_centers, dr_sig_x, dr_sig_y


def _create_do_locations():
    do_deltas = [create_point_2d(300, 400),
                 create_point_2d(0, -100),
                 create_point_2d(-500, 30),
                 create_point_2d(-300, 400),
                 create_point_2d(400, 190),
                 create_point_2d(500, 300)]
    do_sig_x = do_sig_y = Range(30, 30)
    return do_deltas, do_sig_x, do_sig_y


def _create_cd_locations():
    cd_deltas = [create_point_2d(30, 40),
                 create_point_2d(0, -10),
                 create_point_2d(-50, 30),
                 create_point_2d(-30, 40),
                 create_point_2d(40, 20),
                 create_point_2d(50, 30)]
    cd_sig_x = cd_sig_y = Range(10, 10)
    return cd_deltas, cd_sig_x, cd_sig_y


def _create_pdp_locations():
    pdp_deltas = [create_point_2d(4, 5),
                  create_point_2d(2, -1),
                  create_point_2d(-5, 3),
                  create_point_2d(-3, 4),
                  create_point_2d(4, 2),
                  create_point_2d(5, 3)]
    pdp_sig_x = pdp_sig_y = Range(5, 5)
    return pdp_deltas, pdp_sig_x, pdp_sig_y


def create_example_dr_distribution():
    dr_centers, dr_sig_x, dr_sig_y = _create_dr_locations()
    do_deltas, do_sig_x, do_sig_y = _create_do_locations()
    cd_deltas, cd_sig_x, cd_sig_y = _create_cd_locations()
    pdp_deltas, pdp_sig_x, pdp_sig_y = _create_pdp_locations()
    dr_distrib = build_delivery_request_distribution(
        relative_dr_location_distribution=ChoiceNormalDistribution(dr_centers, dr_sig_x, dr_sig_y),
        relative_do_location_distribution=ChoiceNormalDistribution(do_deltas, do_sig_x, do_sig_y),
        relative_cd_location_distribution=ChoiceNormalDistribution(cd_deltas, cd_sig_x, cd_sig_y),
        relative_pdp_location_distribution=ChoiceNormalDistribution(pdp_deltas, pdp_sig_x, pdp_sig_y))
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=4,
                                                num_of_delivery_options_per_delivery_request=6,
                                                num_of_customer_deliveries_per_delivery_option=5,
                                                num_of_package_delivery_plan_per_customer_delivery=12,
                                                delivery_request_distribution=dr_distrib)
    return DeliveryRequestDatasetGenerator().generate(dr_struct, Random(42))


def create_drone_delivery_dock_distribution(amount=3):
    return DroneLoadingDockDistribution() \
        .choose_rand(random=Random(100), base_location=create_point_2d(-5400, 2000), amount=amount)


def draw_all_delivery_requests(sampled_drs: List[DeliveryRequest]):
    d = create_drawer_2d()
    for dr in sampled_drs:
        add_delivery_request(d, dr)
    d.draw()


def create_operational_graph_from_assets(sampled_drs: [DeliveryRequest],
                                         sampled_drone_loading_dock: [DroneLoadingDock]):
    og = OperationalGraph()
    og.add_delivery_requests(sampled_drs)
    graph_creator.add_locally_connected_dr_graph(og, sampled_drs)
    graph_creator.add_fully_connected_loading_docks(og, sampled_drone_loading_dock)
    return og


def draw_operational_graph(og):
    d = create_drawer_2d()
    add_operational_graph(d, og)
    d.draw()


def visualize_delivery_request_sample():
    sampled_drs = create_example_dr_distribution()
    draw_all_delivery_requests(sampled_drs)


def visualize_operational_graph_sample():
    sampled_drs = create_example_dr_distribution()
    og = create_operational_graph_from_assets(sampled_drs, create_drone_delivery_dock_distribution(5))
    draw_operational_graph(og)


if __name__ == '__main__':
    visualize_delivery_request_sample()