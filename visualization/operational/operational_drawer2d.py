from random import Random

from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest, build_delivery_request_distribution, \
    DeliveryRequestLocationDistribution
from common.entities.delivery_request_generator import DeliveryRequestDatasetStructure, DeliveryRequestDatasetGenerator
from common.entities.disribution.distribution import Range
from common.entities.package_delivery_plan import PackageDeliveryPlan
from geometry.geo_distribution import ChoiceNormalDistribution
from geometry.geo_factory import create_line_string_2d, create_point_2d
from visualization.basic.color import Color
from visualization.basic.drawer2d import Drawer2D
from visualization.basic.pltdrawer2d import create_drawer_2d


def add_pdp(drawer: Drawer2D, pdp: PackageDeliveryPlan, draw_internal=True):
    drawer.add_point2d(pdp.drop_point, facecolor=Color.Black, edgecolor=Color.DarkOliveGreen)
    if draw_internal:
        tail_point = pdp.drop_point.add_vector(pdp.azimuth.to_direction())
        drawer.add_arrow2d(tail=tail_point, head=pdp.drop_point, linewidth=2, edgecolor=Color.Green)


def add_cd(drawer: Drawer2D, cd: CustomerDelivery, draw_internal=True):
    drawer.add_polygon2d(cd.calc_bounds(), edgecolor=Color.DarkBlue, facecolor=Color.Blue)
    if draw_internal:
        for pdp in cd.package_delivery_plans:
            add_pdp(drawer, pdp, draw_internal=True)


def add_do(drawer: Drawer2D, do: DeliveryOption, draw_internal=True):
    drawer.add_point2d(do.calc_location(), edgecolor=Color.Red, facecolor=Color.Red, linewidth=5)
    if draw_internal:
        for cd in do.customer_deliveries:
            add_cd(drawer, cd, draw_internal=True)
            drawer.add_point2d(cd.calc_location(), edgecolor=Color.Red, linewidth=2)
            segment = create_line_string_2d([do.calc_location(), cd.calc_location()])
            drawer.add_line_string2d(segment, edgecolor=Color.Red, linewidth=2)


def add_dr(drawer: Drawer2D, dr: DeliveryRequest, draw_internal=True):
    drawer.add_point2d(dr.calc_location(), edgecolor=Color.Black, facecolor=Color.Purple, linewidth=16)
    if draw_internal:
        for do in dr.delivery_options:
            drawer.add_point2d(do.calc_location(), edgecolor=Color.Purple, linewidth=2)
            segment = create_line_string_2d([do.calc_location(), dr.calc_location()])
            drawer.add_line_string2d(segment, edgecolor=Color.Purple, linewidth=2)
            add_do(drawer, do, draw_internal=True)


if __name__ == '__main__':
    d = create_drawer_2d()
    dr_centers = [create_point_2d(4000, 500),
                  create_point_2d(0, -6000),
                  create_point_2d(-5000, 450),
                  create_point_2d(-6000, 2000),
                  create_point_2d(4200, 1900),
                  create_point_2d(5000, 300)]
    dr_sig_x = dr_sig_y = Range(100, 100)

    do_deltas = [create_point_2d(300, 400),
                 create_point_2d(0, -100),
                 create_point_2d(-500, 30),
                 create_point_2d(-300, 400),
                 create_point_2d(400, 190),
                 create_point_2d(500, 300)]
    do_sig_x = do_sig_y = Range(30, 30)

    cd_deltas = [create_point_2d(30, 40),
                 create_point_2d(0, -10),
                 create_point_2d(-50, 30),
                 create_point_2d(-30, 40),
                 create_point_2d(40, 20),
                 create_point_2d(50, 30)]
    cd_sig_x = cd_sig_y = Range(10, 10)

    pdp_deltas = [create_point_2d(4, 5),
                  create_point_2d(2, -1),
                  create_point_2d(-5, 3),
                  create_point_2d(-3, 4),
                  create_point_2d(4, 2),
                  create_point_2d(5, 3)]
    pdp_sig_x = pdp_sig_y = Range(5, 5)

    location_distribution = DeliveryRequestLocationDistribution(
        ChoiceNormalDistribution(dr_centers, dr_sig_x, dr_sig_y),
        ChoiceNormalDistribution(do_deltas, do_sig_x, do_sig_y),
        ChoiceNormalDistribution(cd_deltas, cd_sig_x, cd_sig_y),
        ChoiceNormalDistribution(pdp_deltas, pdp_sig_x, pdp_sig_y))

    dr_distrib = build_delivery_request_distribution(location_distribution)
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=4,
                                                num_of_delivery_options_per_delivery_request=6,
                                                num_of_customer_deliveries_per_delivery_option=5,
                                                num_of_package_delivery_plan_per_customer_delivery=12,
                                                delivery_request_distribution=dr_distrib)
    drs = DeliveryRequestDatasetGenerator().generate(dr_struct, Random(42))
    for dr in drs:
        add_dr(d, dr)
    d.draw()
