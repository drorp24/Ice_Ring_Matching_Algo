import random

from common.entities.base_entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.base_entities.temporal import TimeWindowExtension
from visualization.basic.color import Color
from visualization.basic.gantt_drawer import GanttDrawer


def generate_matched_request_bar_colors() -> [Color]:
    matched_request_bar_colors = list(Color)
    matched_request_bar_colors.remove(Color.White)
    matched_request_bar_colors.remove(Color.Red)
    matched_request_bar_colors.remove(Color.Grey)
    matched_request_bar_colors.remove(Color.Orange)
    random.shuffle(matched_request_bar_colors)
    return matched_request_bar_colors


UNMATCHED_ROW_NUMBER = 1
MATCHED_REQUEST_BAR_COLORS = generate_matched_request_bar_colors()
OPERATING_TIME_WINDOW_COLOR = Color.Red


def add_delivery_board_with_row_per_edd(drawer: GanttDrawer, board: DroneDeliveryBoard, draw_unmatched=True):
    formations = list(set(delivery.delivering_drones.id for delivery in board.drone_deliveries))
    for i, delivery in enumerate(board.drone_deliveries):
        delivery_row = formations.index(delivery.delivering_drones.id) + 1 + UNMATCHED_ROW_NUMBER
        max_inner_rows = max(
            delivery.delivering_drones.drone_formation.get_package_type_amount_map().get_package_type_amounts())
        if len(delivery.matched_requests) == 0:
            continue
        drawer.add_row_area(
            row=delivery_row,
            time_window=TimeWindowExtension(delivery.start_drone_loading_docks.delivery_time_window.since,
                                            delivery.end_drone_loading_docks.delivery_time_window.since),
            edgecolor=OPERATING_TIME_WINDOW_COLOR)
        for request_index, request in enumerate(delivery.matched_requests):
            bar_color = Color.White
            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_time_window.since,
                side_text=str(request.delivery_request.priority),
                color=bar_color,
                inner_row=request_index,
                max_inner_rows=max_inner_rows
            )

    if draw_unmatched:
        _add_unmatched_requests(board, drawer)


def _add_unmatched_requests(board, drawer):
    num_of_unmatched_delivery_requests = len(board.unmatched_delivery_requests)
    max_inner_rows = num_of_unmatched_delivery_requests if num_of_unmatched_delivery_requests > 3 else 3
    for i, unmatched in enumerate(board.unmatched_delivery_requests):
        drawer.add_bar(
            row=UNMATCHED_ROW_NUMBER,
            time_window=unmatched.delivery_request.time_window,
            name="unmatched" + str(i),
            time_mark=None,
            side_text=str(unmatched.delivery_request.priority),
            color=Color.Red,
            inner_row=i,
            max_inner_rows=max_inner_rows
        )


def add_delivery_board_with_row_per_drone_delivery(drawer: GanttDrawer, board: DroneDeliveryBoard, draw_unmatched=True):
    for i, delivery in enumerate(board.drone_deliveries):
        delivery_row = i + 1 + UNMATCHED_ROW_NUMBER
        max_inner_rows = max(

            delivery.delivering_drones.drone_formation.get_package_type_amount_map().get_package_type_amounts())
        if len(delivery.matched_requests) == 0:
            continue
        drawer.add_row_area(
            row=delivery_row,
            time_window=TimeWindowExtension(delivery.start_drone_loading_docks.delivery_time_window.since,
                                            delivery.end_drone_loading_docks.delivery_time_window.since),
            edgecolor=OPERATING_TIME_WINDOW_COLOR)
        for request_index, request in enumerate(delivery.matched_requests):
            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_time_window.since,
                side_text=str(request.delivery_request.priority),
                color=MATCHED_REQUEST_BAR_COLORS[request.graph_index % len(MATCHED_REQUEST_BAR_COLORS)],
                inner_row=request_index,
                max_inner_rows=max_inner_rows
            )

    if draw_unmatched:
        _add_unmatched_requests(board, drawer)
