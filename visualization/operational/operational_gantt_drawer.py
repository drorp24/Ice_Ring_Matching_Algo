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


def add_delivery_board(drawer: GanttDrawer, board: DroneDeliveryBoard, draw_unmatched=True, aggregate_by_edd: bool = True):
    if aggregate_by_edd:
        formations = list(set(delivery.id for delivery in board.drone_deliveries))
    for i, delivery in enumerate(board.drone_deliveries):
        if aggregate_by_edd:
            delivery_row = formations.index(delivery.id) + 1 + UNMATCHED_ROW_NUMBER
        else:
            delivery_row = i + 1 + UNMATCHED_ROW_NUMBER
        if len(delivery.matched_requests) == 0:
            continue
        drawer.add_row_area(
            row=delivery_row,
            time_window=TimeWindowExtension(delivery.start_drone_loading_docks.delivery_time_window.since,
                                            delivery.end_drone_loading_docks.delivery_time_window.since),
            edgecolor=OPERATING_TIME_WINDOW_COLOR)
        for request in delivery.matched_requests:
            if aggregate_by_edd:
                bar_color = color=Color.White
            else:
                bar_color = MATCHED_REQUEST_BAR_COLORS[request.graph_index % len(MATCHED_REQUEST_BAR_COLORS)]

            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_time_window.since,
                side_text=str(request.delivery_request.priority),
                color=bar_color)

    if draw_unmatched:
        for i, unmatched in enumerate(board.unmatched_delivery_requests):
            drawer.add_bar(
                row=UNMATCHED_ROW_NUMBER,
                time_window=unmatched.delivery_request.time_window,
                name="unmatched" + str(i),
                time_mark=None,
                side_text=str(unmatched.delivery_request.priority),
                color=Color.Red)
