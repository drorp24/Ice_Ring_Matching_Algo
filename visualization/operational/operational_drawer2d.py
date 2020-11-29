from random import Random

from common.entities.customer_delivery import CustomerDelivery, CustomerDeliveryDistribution
from common.entities.delivery_option import DeliveryOption, DeliveryOptionDistribution
from common.entities.delivery_request import DeliveryRequest, DeliveryRequestDistribution, generate_dr_distribution
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
            add_pdp(drawer, pdp, draw_internal=False)


def add_do(drawer: Drawer2D, do: DeliveryOption, draw_internal=True):
    drawer.add_point2d(do.calc_location(), edgecolor=Color.Red, linewidth=5)
    if draw_internal:
        for cd in do.customer_deliveries:
            add_cd(drawer, cd, draw_internal=False)
            drawer.add_point2d(cd.calc_location(), edgecolor=Color.Red, linewidth=2)
            segment = create_line_string_2d([do.calc_location(), cd.calc_location()])
            drawer.add_line_string2d(segment, edgecolor=Color.Red, linewidth=4)


def add_dr(drawer: Drawer2D, dr: DeliveryRequest, draw_internal=True):
    drawer.add_point2d(dr.calc_location(), edgecolor=Color.Purple, linewidth=16)
    if draw_internal:
        for do in dr.delivery_options:
            add_do(drawer, do, draw_internal=True)


if __name__ == '__main__':
    # d = create_drawer_2d()
    # pdps = PackageDeliveryPlanDistribution(
    #     azimuth_distribution=AngleUniformDistribution(
    #         start_angle=Angle(0, AngleUnit.DEGREE),
    #         end_angle=Angle(90, AngleUnit.DEGREE))).choose_rand(Random(42), 100)
    # for pdp in pdps:
    #     add_pdp(d, pdp)
    # d.draw()

    # d = create_drawer_2d()
    # cds = CustomerDeliveryDistribution().choose_rand(Random(42), 3, 5)
    #
    # for cd in cds:
    #     add_cd(d, cd)
    # d.draw()

    # d = create_drawer_2d()
    # dos = DeliveryOptionDistribution().choose_rand(random=Random(42), amount=2, num_cd=4, num_pdp=3)
    # for do in dos:
    #     add_do(d, do)
    # d.draw()

    d = create_drawer_2d()
    centers = [create_point_2d(100, 50),
               create_point_2d(0, -100),
               create_point_2d(-200, 45),
               create_point_2d(-300, 100),
               create_point_2d(40, 190),
               create_point_2d(500, 300)]
    sig_x = sig_y = Range(20, 40)
    dr_distrib = generate_dr_distribution(drop_point_distribution=ChoiceNormalDistribution(centers, sig_x, sig_y))
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=6,
                                                num_of_delivery_options_per_delivery_request=4,
                                                num_of_customer_deliveries_per_delivery_option=6,
                                                num_of_package_delivery_plan_per_customer_delivery=7,
                                                delivery_request_distribution=dr_distrib)
    drs = DeliveryRequestDatasetGenerator().generate(dr_struct, Random(42))
    for dr in drs:
        add_dr(d, dr)
    d.draw()
