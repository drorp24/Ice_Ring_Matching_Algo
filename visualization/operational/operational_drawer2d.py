import random

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_delivery import DroneDelivery
from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard, UnmatchedDeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.base_entities.zone import Zone
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
    except...:
        print("drawing error - problem adding customer delivery")
    if draw_internal:
        for pdp in cd.package_delivery_plans:
            add_package_delivery_plan(drawer, pdp, draw_internal=True)


def add_delivery_option(drawer: Drawer2D, do: DeliveryOption, draw_internal=True, color: Color = Color.Red):
    patch = drawer.add_point2d(do.calc_location(), edgecolor=color, facecolor=color, linewidth=1)
    if draw_internal:
        for cd in do.customer_deliveries:
            add_customer_delivery(drawer, cd, draw_internal=True)
            drawer.add_point2d(cd.calc_location(), edgecolor=color, linewidth=2)
            segment = create_line_string_2d([do.calc_location(), cd.calc_location()])
            drawer.add_line_string2d(segment, edgecolor=color, linewidth=2)
    return patch


def add_delivery_request(drawer: Drawer2D, dr: DeliveryRequest, draw_internal=True, color: Color = Color.Green,
                         radius=0.05):
    drawer.add_point2d(dr.calc_location(), radius=radius, edgecolor=color, facecolor=color, linewidth=1)
    if draw_internal:
        for do in dr.delivery_options:
            drawer.add_point2d(do.calc_location(), edgecolor=color, linewidth=2)
            segment = create_line_string_2d([do.calc_location(), dr.calc_location()])
            drawer.add_line_string2d(segment, edgecolor=color, linewidth=2)
            add_delivery_option(drawer, do, draw_internal=True)


def add_drone_loading_dock(drawer: Drawer2D, ds: DroneLoadingDock):
    drawer.add_point2d(ds.calc_location(), edgecolor=Color.Black, facecolor=Color.DodgerBlue, linewidth=5)


def add_operational_graph(drawer: Drawer2D, op_gr: OperationalGraph, draw_internal=True, draw_edges: bool = True,
                          radius=0.05):
    if draw_internal:
        for node in op_gr.nodes:
            if node.internal_type is DeliveryRequest:
                add_delivery_request(drawer, node.internal_node, False, radius=radius)
            elif node.internal_type is DroneLoadingDock:
                add_drone_loading_dock(drawer, node.internal_node)

    if draw_edges:
        [drawer.add_arrow2d(head=edge.start_node.internal_node.calc_location(),
                            tail=edge.end_node.internal_node.calc_location(),
                            edgecolor=_get_color_of_graph_edge(edge), linewidth=1) for edge in op_gr.edges]


def add_zones(drawer: Drawer2D, zones: [Zone]):
    list(map(lambda zone: drawer.add_polygon2d(zone.region, edgecolor=Color.DarkBlue, facecolor=Color.Blue), zones))


def _get_color_of_graph_edge(edge: OperationalEdge):
    cond_color_map = {
        lambda edge_: edge.end_node.internal_type is DroneLoadingDock: Color.Red,
        lambda edge_: edge.start_node.internal_type is DroneLoadingDock: Color.Green,
        lambda edge_: edge.start_node.internal_type is DeliveryRequest
                      and edge.end_node.internal_type is DeliveryRequest: Color.Grey
    }
    for cond in cond_color_map:
        if cond(edge):
            return cond_color_map[cond]


def add_drone_delivery(drawer: Drawer2D, delivery: DroneDelivery, delivery_color: Color):
    locations = []
    delivery_patches = []
    add_drone_loading_dock(drawer, delivery.start_drone_loading_dock.drone_loading_dock)
    locations.append(delivery.start_drone_loading_dock.drone_loading_dock.calc_location())
    for request in delivery.matched_requests:
        matched_delivery_option = request.delivery_request.delivery_options[request.matched_delivery_option_index]
        delivery_patches.append(add_delivery_option(drawer, matched_delivery_option,
                                                    draw_internal=False,
                                                    color=delivery_color))
        current_location = matched_delivery_option.calc_location()
        locations.append(current_location)
    add_drone_loading_dock(drawer, delivery.end_drone_loading_dock.drone_loading_dock)
    locations.append(delivery.end_drone_loading_dock.drone_loading_dock.calc_location())
    return delivery_patches


class _MatchedDeliveryLabelsHandler:
    def __init__(self):
        self._optional_delivery_colors = list(Color)
        self._optional_delivery_colors.remove(Color.Red)
        random.shuffle(self._optional_delivery_colors)
        self.selected_delivery_colors = []
        self.matched_delivery_labels = []
        self.delivery_patches = []

    def add_matched_delivery(self, session_index: int, delivery: DroneDelivery) -> Color:
        self.matched_delivery_labels.append(

            "[" + (delivery.delivering_drones.start_loading_dock.id.display_name(5)) + "]_" +
            "[" + str(delivery.delivering_drones.id.display_name(5)) + "]_ [" + str(session_index) + "]")

        delivery_color = self._optional_delivery_colors[
            len(self.selected_delivery_colors) % len(self._optional_delivery_colors)]
        self.selected_delivery_colors.append(delivery_color)
        return delivery_color


def add_unmatched_delivery_requests(drawer: Drawer2D, unmatched_requests: [UnmatchedDeliveryRequest]):
    for unmatched in unmatched_requests:
        add_delivery_request(drawer, unmatched.delivery_request, draw_internal=False, color=Color.Red)


def add_drone_deliveries(drawer: Drawer2D, board: DroneDeliveryBoard):
    labels_handler = _MatchedDeliveryLabelsHandler()
    for i, delivery in enumerate(board.drone_deliveries):
        if len(delivery.matched_requests) == 0:
            continue
        session_index = board.get_drone_deliveries_by_delivering_drones(
            delivering_drones=delivery.delivering_drones).index(delivery)
        delivery_color = labels_handler.add_matched_delivery(session_index,delivery)
        labels_handler.delivery_patches.append(add_drone_delivery(drawer, delivery, delivery_color))
    drawer.add_legend(labels_handler.matched_delivery_labels, labels_handler.selected_delivery_colors,
                      patches_list=labels_handler.delivery_patches)


def add_delivery_board(drawer: Drawer2D, board: DroneDeliveryBoard, draw_unmatched=True):
    if draw_unmatched:
        add_unmatched_delivery_requests(drawer, board.unmatched_delivery_requests)
    add_drone_deliveries(drawer, board)
