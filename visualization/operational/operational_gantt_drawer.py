import random

from common.entities.drone_delivery_board import DroneDeliveryBoard
from visualization.basic.color import Color
from visualization.basic.gantt_drawer import GanttDrawer


def add_delivery_board(drawer: GanttDrawer, board: DroneDeliveryBoard, draw_dropped=True):
    if draw_dropped:
        dropped_row_num = 1
        for i, dropped in enumerate(board.dropped_delivery_requests):
            drawer.add_bar(
                row=dropped_row_num,
                time_window=dropped.delivery_request.time_window,
                name="dropped" + str(i),
                time_mark=None,
                side_text=str(dropped.delivery_request.priority),
                color=Color.Red)
    for i, delivery in enumerate(board.drone_deliveries):
        if len(delivery.matched_requests) is 0:
            continue
        delivery_row = i + 1 + dropped_row_num
        for request in delivery.matched_requests:
            drawer.add_bar(
                row=delivery_row,
                time_window=request.delivery_request.time_window,
                name=str(request.graph_index),
                time_mark=request.delivery_min_time,
                side_text=str(request.delivery_request.priority),
                color=random.choice(list(Color)))
