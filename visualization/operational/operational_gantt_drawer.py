import random

from common.entities.drone_delivery_board import DroneDeliveryBoard
from common.entities.temporal import TimeWindowExtension
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


DROPPED_ROW_NUMBER = 1
MATCHED_REQUEST_BAR_COLORS = generate_matched_request_bar_colors()


def add_delivery_board(drawer: GanttDrawer, board: DroneDeliveryBoard, draw_dropped=True):
    for i, delivery in enumerate(board.drone_deliveries):
        if len(delivery.matched_requests) is 0:
            continue
        delivery_row = i + 1 + DROPPED_ROW_NUMBER
        drawer.add_row_background_area(
            row=delivery_row,
            time_window=TimeWindowExtension(drawer.get_zero_time(),
                                            delivery.start_drone_loading_docks.delivery_min_time),
            color=Color.Orange)
        drawer.add_row_background_area(
            row=delivery_row,
            time_window=TimeWindowExtension(delivery.end_drone_loading_docks.delivery_min_time,
                                            drawer.get_end_time()),
            color=Color.Orange)
        for request in delivery.matched_requests:
            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_min_time,
                side_text=str(request.delivery_request.priority),
                color=MATCHED_REQUEST_BAR_COLORS[request.graph_index])
    if draw_dropped:
        for i, dropped in enumerate(board.dropped_delivery_requests):
            drawer.add_bar(
                row=DROPPED_ROW_NUMBER,
                time_window=dropped.delivery_request.time_window,
                name="dropped" + str(i),
                time_mark=None,
                side_text=str(dropped.delivery_request.priority),
                color=Color.Red)
