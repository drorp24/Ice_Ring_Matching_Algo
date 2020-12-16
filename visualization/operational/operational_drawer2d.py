from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.graph.operational.operational_graph import OperationalGraph, OperationalEdge
from geometry.geo_factory import create_line_string_2d
from visualization.basic.color import Color
from visualization.basic.drawer2d import Drawer2D


def add_package_delivery_plan(drawer: Drawer2D, pdp: PackageDeliveryPlan, draw_internal=True):
    drawer.add_point2d(pdp.drop_point, facecolor=Color.Black, edgecolor=Color.DarkOliveGreen)
    if draw_internal:
        tail_point = pdp.drop_point.add_vector(pdp.azimuth.to_direction())
        drawer.add_arrow2d(tail=tail_point, head=pdp.drop_point, linewidth=2, edgecolor=Color.Green)


def add_customer_delivery(drawer: Drawer2D, cd: CustomerDelivery, draw_internal=True):
    try:
        drawer.add_polygon2d(cd.calc_bounds(), edgecolor=Color.DarkBlue, facecolor=Color.Blue)
    except:
        print('draw')
    if draw_internal:
        for pdp in cd.package_delivery_plans:
            add_package_delivery_plan(drawer, pdp, draw_internal=True)


def add_delivery_option(drawer: Drawer2D, do: DeliveryOption, draw_internal=True):
    drawer.add_point2d(do.calc_location(), edgecolor=Color.Red, facecolor=Color.Red, linewidth=5)
    if draw_internal:
        for cd in do.customer_deliveries:
            add_customer_delivery(drawer, cd, draw_internal=True)
            drawer.add_point2d(cd.calc_location(), edgecolor=Color.Red, linewidth=2)
            segment = create_line_string_2d([do.calc_location(), cd.calc_location()])
            drawer.add_line_string2d(segment, edgecolor=Color.Red, linewidth=2)


def add_delivery_request(drawer: Drawer2D, dr: DeliveryRequest, draw_internal=True):
    drawer.add_point2d(dr.calc_location(), edgecolor=Color.Black, facecolor=Color.Purple, linewidth=16)
    if draw_internal:
        for do in dr.delivery_options:
            drawer.add_point2d(do.calc_location(), edgecolor=Color.Purple, linewidth=2)
            segment = create_line_string_2d([do.calc_location(), dr.calc_location()])
            drawer.add_line_string2d(segment, edgecolor=Color.Purple, linewidth=2)
            add_delivery_option(drawer, do, draw_internal=True)


def add_drone_loading_dock(drawer: Drawer2D, ds: DroneLoadingDock):
    drawer.add_point2d(ds.calc_location(), edgecolor=Color.Black, facecolor=Color.DodgerBlue, linewidth=5)


def add_operational_graph(drawer: Drawer2D, op_gr: OperationalGraph, draw_internal=True):
    if draw_internal:
        for node in op_gr.nodes:
            if node.internal_type is DeliveryRequest:
                add_delivery_request(drawer, node.internal_node, False)
            elif node.internal_type is DroneLoadingDock:
                add_drone_loading_dock(drawer, node.internal_node)

    [drawer.add_arrow2d(head=edge.start_node.internal_node.calc_location(),
                        tail=edge.end_node.internal_node.calc_location(),
                        edgecolor=_get_color_of_graph_edge(edge), linewidth=1) for edge in op_gr.edges]


def _get_color_of_graph_edge(edge: OperationalEdge):
    cond_color_map = {lambda edge: edge.end_node.internal_type is DroneLoadingDock: Color.Red,
                      lambda edge: edge.start_node.internal_type is DroneLoadingDock: Color.Green,
                      lambda edge: edge.start_node.internal_type is DeliveryRequest and
                                   edge.end_node.internal_type is DeliveryRequest: Color.Grey}
    for cond in cond_color_map:
        if cond(edge):
            return cond_color_map[cond]


def add_delivery_board(drawer: Drawer2D, board: DroneDeliveryBoard, draw_internal=True):
    for delivery in board.drone_deliveries:
        if len(delivery.matched_requests) is 0:
            continue
        locations = []
        add_drone_loading_dock(drawer, delivery.start_drone_loading_docks.drone_loading_dock)
        locations.append(delivery.start_drone_loading_docks.drone_loading_dock.calc_location())
        for request in delivery.matched_requests:
            matched_delivery_option = request.delivery_request.delivery_options[request.matched_delivery_option_index]
            add_delivery_option(drawer, matched_delivery_option, draw_internal=False)
            current_location = matched_delivery_option.calc_location()
            drawer.add_text(str(request.graph_index), current_location, fontsize=17)
            locations.append(current_location)
        add_drone_loading_dock(drawer, delivery.end_drone_loading_docks.drone_loading_dock)
        locations.append(delivery.end_drone_loading_docks.drone_loading_dock.calc_location())
        for i, location in enumerate(locations[:-1]):
            drawer.add_arrow2d(head=locations[i+1], tail=locations[i], edgecolor=Color.Blue, linewidth=2)
