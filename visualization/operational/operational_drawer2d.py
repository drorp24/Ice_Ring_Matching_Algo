from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package_delivery_plan import PackageDeliveryPlan
from geometry.geo_factory import create_line_string_2d
from visualization.basic.color import Color
from visualization.basic.drawer2d import Drawer2D


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
