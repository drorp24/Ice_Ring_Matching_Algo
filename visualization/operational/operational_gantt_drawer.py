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


def add_delivery_board(drawer: GanttDrawer, board: DroneDeliveryBoard, draw_unmatched=True):
    for i, delivery in enumerate(board.drone_deliveries):
        delivery_row = i + 1 + UNMATCHED_ROW_NUMBER
        if len(delivery.matched_requests) is 0:
            continue
        drawer.add_row_area(
            row=delivery_row,
            time_window=TimeWindowExtension(delivery.start_drone_loading_docks.delivery_min_time,
                                            delivery.end_drone_loading_docks.delivery_min_time),
            edgecolor=OPERATING_TIME_WINDOW_COLOR)
        for request in delivery.matched_requests:
            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_min_time,
                side_text=str(request.delivery_request.priority),
                color=MATCHED_REQUEST_BAR_COLORS[request.graph_index % len(MATCHED_REQUEST_BAR_COLORS)])
    if draw_unmatched:
        for i, unmatched in enumerate(board.unmatched_delivery_requests):
            drawer.add_bar(
                row=UNMATCHED_ROW_NUMBER,
                time_window=unmatched.delivery_request.time_window,
                name="unmatched" + str(i),
                time_mark=None,
                side_text=str(unmatched.delivery_request.priority),
                color=Color.Red)
